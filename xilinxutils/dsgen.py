class BaseType:
    """
    Abstract base for all types.

    Parameters
    ----------
    width : int
        Bitwidth of the type.
    """
    def __init__(
            self, 
            width: int):
        self.width = width
   
    def cpp_repr(self) -> str:
        raise NotImplementedError
    
    def read_expr(self,
                  word_name: str,
                  word_width: int = 32,
                  ind0 : int = 0) -> str:
        """
        Generate C++ expression to read this type from a word of type ap_unit<word_width>.

        Parameters
        ----------
        word_name : str
            Name of the variable representing the word to read from.
        word_width : int
            Bitwidth of the word type.
        ind0 : int, optional
            Starting bit index within the word to read from.
        """
        if self.width + ind0 > word_width:
            raise ValueError("Type bitwidth exceeds word bitwidth at given index.")
        return self.read_expr_impl(word_name, word_width, ind0)
    
    def read_expr_impl(self,
                       word_name: str,
                       word_width: int,
                       ind0 : int) -> str:
        raise NotImplementedError   
    
    def write_expr(self,
                   var_name: str,
                   word_name: str,
                   word_width: int = 32,
                   ind0: int = 0) -> str:
        """
        Generate C++ expression to write this type into a word of type ap_uint<word_width>.

        Parameters
        ----------
        var_name : str
            Name of the variable holding the field value.
        word_name : str
            Name of the variable representing the destination word.
        word_width : int
            Bitwidth of the word type.
        ind0 : int, optional
            Starting bit index within the word to write into.
        """
        if self.width + ind0 > word_width:
            raise ValueError("Type bitwidth exceeds word bitwidth at given index.")
        return self.write_expr_impl(var_name, word_name, word_width, ind0)

    def write_expr_impl(self,
                        var_name: str,
                        word_name: str,
                        word_width: int,
                        ind0: int) -> str:
        raise NotImplementedError
    
    def preamble(self) -> str:
        """
        Returns any necessary C++ preamble code for this type.  This code will be added
        at the top of the class definition.

        Returns
        -------
        str | None
            C++ code snippet.  If None or empty, no preamble is added.
        """
        return None

    
class IntType(BaseType):
    """
    Arbitrary precision integer type (ap_int/ap_uint).

    Parameters
    ----------
    width : int
        Bitwidth of the integer.
    signed : bool, optional
        Whether the integer is signed (default True).
    """

    def __init__(self, width: int, signed: bool = True):
        super().__init__(width)
        if width <= 0:
            raise ValueError("Width must be positive")
        self.signed = signed

    def cpp_repr(self) -> str:
        """
        Returns
        -------
        str
            C++ type string for this integer.
        """
        base = "ap_int" if self.signed else "ap_uint"
        return f"{base}<{self.width}>"

    def read_expr_impl(self,
                       word_name: str,
                       word_width: int,
                       ind0: int) -> str:
        """
        Generate C++ expression to read this integer from a word.

        Returns
        -------
        str
            C++ code snippet (expression only).
        """
        if self.width == word_width and ind0 == 0:
            # Direct assignment if the field fills the whole word
            return f"{word_name}"
        else:
            # Slice assignment
            high = ind0 + self.width - 1
            return f"{word_name}.range({high}, {ind0})"

    def write_expr_impl(self,
                        var_name: str,
                        word_name: str,
                        word_width: int,
                        ind0: int) -> str:
        """
        Generate C++ expression to write this integer into a word.

        Returns
        -------
        str
            C++ code snippet (statement).
        """
        if self.width == word_width and ind0 == 0:
            # Direct assignment if the field fills the whole word
            return f"{word_name} = {var_name};"
        else:
            # Slice assignment
            high = ind0 + self.width - 1
            return f"{word_name}.range({high}, {ind0}) = {var_name};"
        
class FloatType(BaseType):
    """
    32-bit IEEE-754 floating point type.

    Notes
    -----
    - Always uses 32 bits.
    - Conversion between ap_uint<32> and float is done via a union
      to preserve bit patterns safely in HLS.
    """

    def __init__(self):
        super().__init__(32)

    def cpp_repr(self) -> str:
        """
        Returns
        -------
        str
            C++ type string for this float.
        """
        return "float"

    def read_expr_impl(self,
                       word_name: str,
                       word_width: int,
                       ind0: int) -> str:
        """
        Generate C++ code to read a float from a word.

        Returns
        -------
        str
            C++ code snippet (statement).
        """
        if ind0 + self.width > word_width:
            raise ValueError("Float field does not fit in word")

        # Slice bits if not aligned to full word
        if self.width == word_width and ind0 == 0:
            src_expr = word_name
        else:
            high = ind0 + self.width - 1
            src_expr = f"{word_name}.range({high}, {ind0})"

        return (
            "union { float f; ap_uint<32> u; } conv;\n"
            f"        conv.u = {src_expr};\n"
            f"        /* assign to variable */ conv.f"
        )

    def write_expr_impl(self,
                        var_name: str,
                        word_name: str,
                        word_width: int,
                        ind0: int) -> str:
        """
        Generate C++ code to write a float into a word.

        Returns
        -------
        str
            C++ code snippet (statement).
        """
        if ind0 + self.width > word_width:
            raise ValueError("Float field does not fit in word")

        high = ind0 + self.width - 1
        return (
            "union { float f; ap_uint<32> u; } conv;\n"
            f"        conv.f = {var_name};\n"
            f"        {word_name}.range({high}, {ind0}) = conv.u;"
        )


class EnumType(BaseType):
    """
    Enumeration type.

    Parameters
    ----------
    name : str
        Name of the enum type.
    entries : list
        List of enum entries. Each entry can be a string (auto-assigned value)
        or a tuple (name, value).
    width : int, optional
        Bitwidth of the enum type. If None, calculated from number of entries.
    """
    def __init__(self, 
                 name: str, 
                 entries: list, 
                 width: int = None):
        self.name = name
        self.entries = []
        next_val = 0
        for e in entries:
            if isinstance(e, str):
                self.entries.append((e, next_val))
                next_val += 1
            elif isinstance(e, tuple):
                self.entries.append(e)
                next_val = e[1] + 1
            else:
                raise ValueError("Enum entries must be str or (str, int)")
        if width is None:
            import math
            width = max(1, math.ceil(math.log2(next_val)))
        super().__init__(width)
    
    def cpp_repr(self) -> str:
        """
        Returns
        -------
        str
            C++ type string for this integer.
        """
        return f"ap_uint<{self.width}>"

    def read_expr_impl(self,
                       word_name: str,
                       word_width: int,
                       ind0: int) -> str:
        """
        Generate C++ expression to read this integer from a word.

        Returns
        -------
        str
            C++ code snippet (expression only).
        """
        if self.width == word_width and ind0 == 0:
            # Direct assignment if the field fills the whole word
            return f"{word_name}"
        else:
            # Slice assignment
            high = ind0 + self.width - 1
            return f"{word_name}.range({high}, {ind0})"

    def write_expr_impl(self,
                        var_name: str,
                        word_name: str,
                        word_width: int,
                        ind0: int) -> str:
        """
        Generate C++ expression to write this integer into a word.

        Returns
        -------
        str
            C++ code snippet (statement).
        """
        if self.width == word_width and ind0 == 0:
            # Direct assignment if the field fills the whole word
            return f"{word_name} = {var_name};"
        else:
            # Slice assignment
            high = ind0 + self.width - 1
            return f"{word_name}.range({high}, {ind0}) = {var_name};"

    def preamble(self) -> str:
        """
        Generate C++ enum declaration.

        Returns
        -------
        str
            C++ enum declaration code snippet.
        """
        enumerators = ",\n        ".join(f"{name} = {val}" for name, val in self.entries)
        return f"enum {self.name} : unsigned int {{\n        {enumerators}\n    }};"  


class FieldInfo:
    def __init__(
            self, 
            name: str, 
            dtype: BaseType,
            descr: str = None,
            comment_style: str = "inline"):
        """
        Parameters
        ----------
        name : str
            Name of the field
        dtype : BaseType
            Data type of the field
        descr : str | None
            Optional description of the field
        comment_style : {"inline", "above"}
            Placement of the comment in generated C++ code
        """
        self.name = name
        self.dtype = dtype
        self.descr = descr
        self.comment_style = comment_style

    def cpp_decl(self) -> str:
        if self.descr and self.comment_style == 'above':
            return f"    // {self.descr}\n    {self.dtype.cpp_repr()} {self.name};"
        elif self.descr and self.comment_style == 'inline':
            return f"    {self.dtype.cpp_repr()} {self.name}; // {self.descr}"
        else:
            return f"    {self.dtype.cpp_repr()} {self.name};"
    
class DataStructGen(object):
    """
    Class for generating C++ struct declarations and serialization methods.

    Parameters
    ----------
    name: str
        Name of the data structure.
    fields: List[FieldInfo]
        List of fields in the data structure.
    """
    def __init__(self, 
                 name: str,
                 fields: list[FieldInfo] | None = None):
        self.name = name
        self.fields = fields if fields is not None else []
        self.stream_bus_widths = []

    def add_field(self, field: FieldInfo):
        self.fields.append(field)

    def cpp_decl(self) -> str:
        decl_lines = [f"struct {self.name} {{"]
        for field in self.fields:
            decl_lines.append(field.cpp_decl())
        decl_lines.append("};")
        return "\n".join(decl_lines)
    
    def gen_include(
        self,
        include_file: None | str = None,
        include_dir: None | str = None,
        bus_widths: list[int] | None = None
    ) -> str: 
        """
        Generate and write the C++ include file for this data structure.

        The include file will be of the form:

        #ifndef <INCLUDE_FILE_H>
        #define <INCLUDE_FILE_H>

        class <name> {
            // fields...
            
            // one stream_read function for each bus width
            // one stream_write function for each bus width
            // generic stream_read and stream_write dispatch functions
            // equality operator
            // to_string method
        };

        #endif // <INCLUDE_FILE_H>

        Parameters
        ----------
        include_dir : str
            Directory where the include file is located. The directory will be
            created if needed.
        include_file : None | str
            Name of the include file. If None, defaults to <name>.h
        bus_widths : list[int] | None
            List of bus widths to generate stream functions for.
            If None, defaults to [32].

        Returns
        -------
        str
            Full path to the generated include file.
        """
        import os
        
        # Set defaults
        if include_dir is None:
            include_dir = os.getcwd()
        if include_file is None:
            include_file = f"{self.name.lower()}.h"
        if bus_widths is None:
            bus_widths = [32]
        
        # Store bus widths for dispatch method generation
        self.stream_bus_widths = bus_widths
        
        # Create include directory if it doesn't exist
        os.makedirs(include_dir, exist_ok=True)
        
        # Delete existing file if it exists
        file_path = os.path.join(include_dir, include_file)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Generate include guard macro name
        guard_name = include_file.upper().replace('.', '_').replace('-', '_')
        
        # Build the file content
        lines = []
        
        # Include guard start
        lines.append(f"#ifndef {guard_name}")
        lines.append(f"#define {guard_name}")
        lines.append("")
        
        # Include necessary headers
        lines.append("#include <hls_stream.h>")
        lines.append("#include <ap_int.h>")
        lines.append("#include <ap_axi_sdata.h>")
        lines.append("#include <string>")
        lines.append("#include <sstream>")
        lines.append("")
        
        # Struct declaration with fields
        lines.append(f"class {self.name} {{")
        lines.append("public:")
        lines.append("")
        
        # Add preambles for fields that have them
        for field in self.fields:
            preamble = field.dtype.preamble()
            if preamble is not None and preamble.strip():
                lines.append(f"    {preamble}")
                lines.append("")
    
        for field in self.fields:
            lines.append(field.cpp_decl())
        lines.append("")
        
        # Generate stream functions for each bus width
        for bus_width in bus_widths:
            # Generate stream_read
            lines.append(self.gen_stream_read(bus_width))
            lines.append("")
            
            # Generate stream_write
            lines.append(self.gen_stream_write(bus_width))
            lines.append("")

        # Generate generic dispatch methods
        stream_write_dispatch, stream_read_dispatch = self.gen_stream_dispatch()
        lines.append(stream_write_dispatch)
        lines.append("")
        lines.append(stream_read_dispatch)
        lines.append("")
        
        # Generate equality operator
        lines.append(self.gen_equality_operator())
        lines.append("")
        
        # Generate to_string method
        lines.append(self.gen_string_method())
        lines.append("")

        # Close struct
        lines.append("};")
        lines.append("")

        # Include guard end
        lines.append(f"#endif // {guard_name}")
        lines.append("")

        # Write to file
        with open(file_path, 'w') as f:
            f.write("\n".join(lines))

        return file_path

    def gen_stream_read(self, bus_width: int = 32) -> str:
        """
        Generate the C++ method for reading this struct from an HLS stream.

        Parameters
        ----------
        bus_bits : int
            Bitwidth of the stream word.

        Returns
        -------
        str
            C++ method definition as a string.
        """
        # Check that no field exceeds bus width
        for f in self.fields:
            if f.dtype.width > bus_width:
                raise ValueError(
                    f"Field '{f.name}' has width {f.dtype.width} bits, "
                    f"which exceeds bus width {bus_width} bits"
                )
    
        lines = []
        lines.append("    template<typename Tstream>")
        lines.append(f"    bool stream_read_{bus_width}(hls::stream<Tstream>& in) {{")
        lines.append(f"        constexpr int bus_bits = decltype(Tstream::data)::width;")
        lines.append(f"        static_assert(bus_bits == {bus_width}, "
                    f"\"Only {bus_width}-bit stream supported in {self.name}::stream_read_{bus_width}\");")
        lines.append("")

        ind0 = 0       # current bit index within the word
        word_count = 0 # count of words read
        word_var = None

        for f in self.fields:
            bw = f.dtype.width

            # If field doesn't fit in current word, read a new one
            if ind0 + bw > bus_width or word_var is None:
                word_var = f"w{word_count}"
                lines.append(f"        Tstream {word_var} = in.read();")
                ind0 = 0
                word_count += 1

            # Generate assignment using field's read_expr
            expr = f.dtype.read_expr(word_var + ".data", bus_width, ind0)
            lines.append(f"        {f.name} = {expr};")

            # Advance bit index
            ind0 += bw

        lines.append(f"        bool tlast = {word_var}.last;")
        lines.append("")
        lines.append("        return tlast;")
        lines.append("    }")
        return "\n".join(lines)

    def gen_stream_write(self, bus_width: int = 32) -> str:
        """
        Generate the C++ method for writing this struct to an HLS stream.

        Parameters
        ----------
        bus_width : int
            Bitwidth of the stream word.

        Returns
        -------
        str
            C++ method definition as a string.
        """
        # Check that no field exceeds bus width
        for f in self.fields:
            if f.dtype.width > bus_width:
                raise ValueError(
                    f"Field '{f.name}' has width {f.dtype.width} bits, "
                    f"which exceeds bus width {bus_width} bits"
                )
    
        lines = []
        lines.append("    template<typename Tstream>")
        lines.append(f"    void stream_write_{bus_width}(hls::stream<Tstream>& out, bool tlast = true) const {{")
        lines.append(f"        constexpr int bus_bits = decltype(Tstream::data)::width;")
        lines.append(f"        static_assert(bus_bits == {bus_width}, "
                    f"\"Only {bus_width}-bit stream supported in {self.name}::stream_write_{bus_width}\");")
        lines.append("")

        ind0 = 0       # current bit index within the word
        word_count = 0 # count of words written
        word_var = None
        total_words = 0  # track total number of words needed

        # First pass: determine total number of words needed
        temp_ind = 0
        temp_count = 0
        for f in self.fields:
            bw = f.dtype.width
            if temp_ind + bw > bus_width or temp_count == 0:
                temp_count += 1
                temp_ind = bw
            else:
                temp_ind += bw
        total_words = temp_count

        # Second pass: generate the write code
        for f in self.fields:
            bw = f.dtype.width

            # If field doesn't fit in current word, write current word and start a new one
            if ind0 + bw > bus_width or word_var is None:
                # Write the previous word if it exists
                if word_var is not None:
                    is_last = word_count == total_words
                    lines.append(f"        {word_var}.last = false;")
                    lines.append(f"        out.write({word_var});")
                    lines.append("")
                
                # Start a new word
                word_count += 1
                word_var = f"w{word_count - 1}"
                lines.append(f"        Tstream {word_var};")
                lines.append(f"        {word_var}.data = 0;")
                lines.append(f"        {word_var}.keep = -1;")
                lines.append(f"        {word_var}.strb = -1;")
                ind0 = 0

            # Generate write expression using field's write_expr
            write_stmt = f.dtype.write_expr(f.name, word_var + ".data", bus_width, ind0)
            lines.append(f"        {write_stmt}")

            # Advance bit index
            ind0 += bw

        # Write the final word
        if word_var is not None:
            lines.append(f"        {word_var}.last = tlast;")
            lines.append(f"        out.write({word_var});")

        lines.append("    }")
        return "\n".join(lines)

    def gen_stream_dispatch(self) -> tuple[str, str]:
        """
        Generate generic stream_read and stream_write dispatch methods.
        
        Returns
        -------
        tuple[str, str]
            (stream_write code, stream_read code)
        """
        
        if not self.stream_bus_widths:
            # If no bus widths are defined, generate methods that always fail at compile time
            write_lines = []
            write_lines.append("    template<typename Tstream>")
            write_lines.append("    void stream_write(hls::stream<Tstream>& out, bool tlast = true) const {")
            write_lines.append("        static_assert(sizeof(Tstream) == 0, ")
            write_lines.append(f"                     \"No stream bus widths configured for {self.name}\");")
            write_lines.append("    }")
            
            read_lines = []
            read_lines.append("    template<typename Tstream>")
            read_lines.append("    bool stream_read(hls::stream<Tstream>& in) {")
            read_lines.append("        static_assert(sizeof(Tstream) == 0, ")
            read_lines.append(f"                     \"No stream bus widths configured for {self.name}\");")
            read_lines.append("        return false;")
            read_lines.append("    }")
            
            return "\n".join(write_lines), "\n".join(read_lines)

        # Generate stream_write dispatch
        write_lines = []
        write_lines.append("    template<typename Tstream>")
        write_lines.append("    void stream_write(hls::stream<Tstream>& out, bool tlast = true) const {")
        write_lines.append("        constexpr int bus_bits = decltype(Tstream::data)::width;")
        
        for i, width in enumerate(self.stream_bus_widths):
            if i == 0:
                write_lines.append(f"        if constexpr (bus_bits == {width}) {{")
            else:
                write_lines.append(f"        }} else if constexpr (bus_bits == {width}) {{")
            write_lines.append(f"            stream_write_{width}(out, tlast);")
        
        write_lines.append("        } else {")
        widths_str = ", ".join(str(w) for w in self.stream_bus_widths)
        write_lines.append(f"            static_assert(bus_bits == {self.stream_bus_widths[0]}, ")
        write_lines.append(f"                         \"Unsupported bus width. Supported widths: {widths_str}\");")
        write_lines.append("        }")
        write_lines.append("    }")
        
        # Generate stream_read dispatch
        read_lines = []
        read_lines.append("    template<typename Tstream>")
        read_lines.append("    bool stream_read(hls::stream<Tstream>& in) {")
        read_lines.append("        constexpr int bus_bits = decltype(Tstream::data)::width;")
        
        for i, width in enumerate(self.stream_bus_widths):
            if i == 0:
                read_lines.append(f"        if constexpr (bus_bits == {width}) {{")
            else:
                read_lines.append(f"        }} else if constexpr (bus_bits == {width}) {{")
            read_lines.append(f"            return stream_read_{width}(in);")
        
        read_lines.append("        } else {")
        read_lines.append(f"            static_assert(bus_bits == {self.stream_bus_widths[0]}, ")
        read_lines.append(f"                         \"Unsupported bus width. Supported widths: {widths_str}\");")
        read_lines.append("            return false;")
        read_lines.append("        }")
        read_lines.append("    }")
        
        return "\n".join(write_lines), "\n".join(read_lines)
    
    def gen_equality_operator(self) -> str:
        """
        Generate C++ equality operator for this struct.

        Returns
        -------
        str
            C++ method definition as a string.
        """
        lines = []
        lines.append(f"    bool operator==(const {self.name}& other) const {{")
        comparisons = [f"(this->{f.name} == other.{f.name})" for f in self.fields]
        lines.append("        return " + " && ".join(comparisons) + ";")
        lines.append("    }")
        return "\n".join(lines)
    
    def gen_string_method(self) -> str:
        """
        Generate C++ method to convert this struct to a string.

        Returns
        -------
        str
            C++ method definition as a string.
        """
        lines = []
        lines.append("    std::string to_string() const {")
        lines.append("        std::ostringstream oss;")
        lines.append('        oss << "{";')
        for i, f in enumerate(self.fields):
            if i < len(self.fields) - 1:
                lines.append(f'        oss << "{f.name}: " << {f.name} << ", ";')
            else:
                lines.append(f'        oss << "{f.name}: " << {f.name};')
        lines.append('        oss << "}";')
        lines.append("        return oss.str();")
        lines.append("    }")
        return "\n".join(lines)