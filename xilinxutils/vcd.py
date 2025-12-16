import matplotlib.pyplot as plt
import numpy as np
from vcdvcd import VCDVCD

class SigInfo(object):
    """
    Class to hold information about a VCD signal.

    Attributes
    ----------
    name : str
        Full name of the signal.
    two_level : bool
        True if the signal is two-level (0 and 1).
    vcd_fmt : str
        Format of the signal in VCD ('str' or 'binary').
        Later we will add numeric formats
    numeric_type  : str
        Type of numeric data ('str', 'int', 'float').
    numeric_fmt_str : str
        Format string for numeric display.  
    is_clock : bool
        True if the signal is identified as a clock.
    values : list of str
        List of signal values from the VCD file
    times : list of int
        List of time points corresponding to the signal values.
    disp_vals : list of str
        List of signals values for display (after formatting).
    short_name : str
        Short name of the signal (e.g., last part of full name).
    """
    def __init__(
            self,
            name : str,
            tv : list[tuple[int, str]],
            time_scale : float = 1e3):
        self.name = name
        self.two_level = False
        self.vcd_fmt = 'str' # 'str' or 'binary'
        self.numeric_type = 'str' # 'str', 'int', 'float', 'hex'
        self.numeric_fmt_str = '%X'  
        self.is_clock = False
        self.time_scale = time_scale

        # Get time and value lists
        n  = len(tv)
        self.times = np.zeros(n, dtype=float)
        self.values = []
        for i, (t, v) in enumerate(tv):
            self.values.append(v)
            self.times[i] = t / self.time_scale  # Scale time
        self.short_name = name.split('.')[-1]
        self.disp_values = None
        self.numeric_values = None

        self.set_format()

    def set_format(self):
        """
        Auto-detects the format of the signal based on its values.
        Right now this only works for Vivado-generated VCDs where the
        values are text strings.  
        
        The format can be over-written later if needed.
        """
    
        # Remove un-specified values
        filtered = [v for v in self.values if v not in {'x', 'X', 'z', 'Z'}]

        # Check if all values are single-bit '0' or '1'
        if all(v in {'0', '1'} for v in filtered):
            self.two_level = True
            self.numeric_type  = 'int'
            self.numeric_fmt_str = '%d'
            self.vcd_fmt = 'binary'

        # Check if all values are strings composed only of '0' and '1's
        elif all(set(v).issubset({'0', '1'}) for v in filtered):
            self.vcd_fmt = 'binary'
            self.numeric_type  = 'int'

        # Check if clock signal
        if self.name:
            name_lower = self.name.lower()
            if 'clock' in name_lower or 'clk' in name_lower:
                self.is_clock = True

    def get_values(self):
        """
        Converts the signal numeric and display values based on the format.   

        Right now, `float` is not implemented.
        """
        self.disp_values = []
        self.numeric_values = []
        for v in self.values:
            d = str(v)  # Default is to  display original value
            num_value = 0
            if not (v in {'x', 'X', 'z', 'Z'}):
                if self.vcd_fmt == 'binary':
                    num_value = int(v, 2)
                    d = self.numeric_fmt_str % num_value                    
            self.numeric_values.append(num_value)
            self.disp_values.append(d)
        self.numeric_values = np.array(self.numeric_values).astype(np.uint32)

    


class VcdViewer(object):
    """
    Class to view VCD signals and plot timing diagrams.

    Attributes
    ----------
    sig_info : dict[str, SigInfo]
        Information for each signal to be processed.
    time_scale : float
        Time scaling factor (default: 1e3 for ns).
    """
    def __init__(
            self, 
            vcd : VCDVCD):
        """
        Parameters
        ----------
        vcd : VCDVCD
            Parsed VCD object to initialize the viewer.
        """

        self.vcd = vcd        
        self.sig_info = dict()
        self.time_scale = 1e3  # default to ns

  
    def add_signal(self, 
                   name : str):
        """ 
        Adds a signal to be processed
        """
        for s in self.vcd.signals:
            if s == name:
                sig_info = SigInfo(name, self.vcd[s].tv, self.time_scale)
                self.sig_info[s] = sig_info                
                return
        raise ValueError(f"Signal '{name}' not found in VCD.")

    def add_saxi_signals(self):
        """ 
        Adds the s_axi_control signals to disp_signals. 
        """
        prefix = 's_axi_control'
        for s in self.vcd.signals:
            if prefix in s:
                short_name = s.split(f"{prefix}_")[-1]
                self.add_signal(s)
                self.sig_info[s].short_name = short_name
       
    def add_clock_signal(
            self, 
            name : str | None = None) -> str:
        """
        Adds a clock signal to sig_info and marks it as a clock.
        Parameters
        ----------
        name : str
            Name that must be contained in the signal along with 'clock' or 'clk' to be added.

        Returns
        -------
        full_name : str
            Full name of the clock signal added.
        """
        for s in self.vcd.signals:
            name_lower = s.lower()
            if (('clock' in name_lower) or ('clk' in name_lower)) and (name is None or name in s):
                name = s
                break
        if name is None:
            raise ValueError("No clock signal found in VCD.")
        self.add_signal(name)
        self.sig_info[name].is_clock = True
        self.sig_info[name].short_name =  'clk'

        return name

    def add_status_signals(
            self, 
            prefix : str ='AESL_'):
        """
        Adds the status signals to disp_signals.

        Following the Vivado HLS naming convention, the signals added 
        are those ending with {prefix} + one of
        'clock', 'start', 'done', 'idle', 'ready'.

        Parameters
        ----------
        prefix : str
            Prefix for the status signals
        """
        suffixes = ['clock', 'start', 'done', 'idle', 'ready']
        for s in self.vcd.signals:
            for suf in suffixes:
                if s.endswith(f"{prefix}{suf}"):
                    self.add_signal(s)
                    self.sig_info[s].short_name = suf

    def add_axiss_signals(
            self,
            name : str | None = None,
            short_name_prefix : str | None = None) -> dict[str, str]:
        """
        Adds signals that are part of an AXI4-Stream interface.

        Parameters
        ----------
        name : str | None
            If provided, only signals containing this substring are considered.
        short_name_prefix : str | None
            If provided, this prefix is added to the short names of the signals.

        Returns
        -------
        axi_sigs : dict[str, str]
            Dictionary mapping AXI4-Stream keywords to signal names.
        bitwidth : int
            Bitwidth of the TDATA signal.
        """
        axi4s_keywords = ['tdata', 'tvalid', 'tready', 'tlast']
        axi_sigs = dict()
        for kw in axi4s_keywords:
            axi_sigs[kw] = None
            for s in self.vcd.signals:
                if kw in s.lower() and (name is None or name in s):
                    if axi_sigs[kw] is not None:
                        raise ValueError(f"Multiple signals found for AXI4-Stream keyword '{kw}'.")
                    axi_sigs[kw] = s
                    self.add_signal(s)
                    if short_name_prefix:
                        short_name = f"{short_name_prefix}_{kw.upper()}"
                    elif name:
                        short_name = f"{name}_{kw.upper()}"
                    else:  
                        short_name = kw.upper()
                    self.sig_info[s].short_name = short_name
            if axi_sigs[kw] is None:
                raise ValueError(f"No signal found for AXI4-Stream keyword '{kw}'.")
            
        # Get the bitwidth from the TDATA signal.
        # The signal ends in [N:0], so the width is N+1
        tdata_sig = axi_sigs['tdata']
        tdata_parts = tdata_sig.split('[')
        bitwidth = None
        if len(tdata_parts) > 1:
            bit_range = tdata_parts[-1].strip(']')
            msb_lsb = bit_range.split(':')
            if len(msb_lsb) == 2:
                msb = int(msb_lsb[0])
                bitwidth = msb + 1       

        if bitwidth is None:
            raise ValueError(f"Could not determine bitwidth from TDATA signal '{tdata_sig}'.")   
                  
        return axi_sigs, bitwidth

   
    def full_name(
            self, 
            short_name : str) -> str:
        """
        Returns the full signal name for a given short name.
        Parameters
        ----------
        short_name : str
            Short name of the signal
        Returns
        -------
        full_name : str
            Full signal name if found, else None
        """
        for s, si in self.sig_info.items():
            if si.short_name == short_name:
                return s
        return None
    
    def get_values(
            self):
        """
        Converts the signal values for all added signals.
        """
        for s, si in self.sig_info.items():
            si.get_values()

    
    
    def plot_signals(
            self,
            short_names = None,
            add_clk_grid = True,
            ax = None,
            fig_width = 10,
            row_height = 0.5,
            row_step = 0.8,
            left_border = None,
            right_border = None,
            trange = None,
            text_scale_factor = 1000):
        """
        Plots the timing diagram for the selected signals.

        Parameters
        ----------
        short_names : list of str, optional
            List of short names of signals to plot. If None, plots all signals.
        add_clk_grid : bool, optional
            If True, adds vertical grid lines at clock edges. 
        ax : matplotlib.axes.Axes, optional
            Axes object to plot on. If None, a new figure and axes are created.
        fig_width : float, optional
            Width of the figure in inches (if ax is None).
        row_height : float, optional    
            Height of each row in inches.  
        row_step : float, optional
            Vertical spacing between rows.
        left_border : float, optional
            Left border space in time units. If None, set to 10% of time range.
        right_border : float, optional
            Right border space in time units. If None, set to 5% of time range.
        trange : tuple(float, float), optional
            Time range (tmin, tmax) to plot. If None, uses full range of signals.
        text_scale_factor : float, optional
            Scale factor to determine if there is enough space to draw text labels.

        Returns 
        -------
        None         
        ax : matplotlib.axes.Axes
            Axes object with the plotted signals.   
        """

        # Determine signals to plot
        if short_names is None:
            signals_to_plot = list(self.sig_info.keys())    
        else:
            sig_found = {sn: False for sn in short_names}
            signals_to_plot = []
            for s, si in self.sig_info.items():
                if si.short_name in short_names:
                    sn = si.short_name  
                    sig_found[sn] = True
                    signals_to_plot.append(s)
            for sn, found in sig_found.items():
                if not found:
                    print(f"Warning: Signal with short name '{sn}' not found.")

        
    
        # Create figure and axis if not provided
        nsig = len(signals_to_plot)
        ymax = row_step * nsig
        if ax is None:
            ax_provided = False
            fig_height = row_height * nsig
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        else:
            ax_provided = True


        # Get min and max times.  If not provided, compute from signals
        if trange is not None:
            tmin, tmax = trange
        else:
            for i, s in enumerate(signals_to_plot):
                si = self.sig_info[s]
                if i == 0:
                    tmin = si.times[0]
                    tmax = si.times[-1]
                else:
                    tmin = min(tmin, si.times[0])
                    tmax = max(tmax, si.times[-1])   

        # Compute the borders if not provided as a fration of total time range
        # Default is left border = 15% of time range, right border = 5% of time range
        # This gives space for signal names on the left
        time_range = tmax - tmin        
        if left_border is None:
            left_border = 0.10 * time_range
        if right_border is None:
            right_border = 0.05 * time_range

        # Save the top and bottom y positions for each signal
        self.ytop = dict()
        self.ybot = dict()

        for i, s in enumerate(signals_to_plot):
            y =  ymax - (i + 0.5) * row_step  # vertical position for signal s
            si = self.sig_info[s]
            t_list = si.times 
            sn = si.short_name

            # Get the display values
            si.get_values()
            v_list = si.disp_values
            
            # Draw signal name
            ax.text(tmin - 0.5, y, sn, ha='right', va='center', fontsize=10)

            # Set the top and bottom y positions for the signal
            ybot = y - 0.4 * row_step
            ytop = y + 0.4 * row_step
            self.ytop[sn] = ytop
            self.ybot[sn] = ybot


            # Draw horizontal segments between value changes
            vlast = None
            for j in range(len(t_list)):
                t_start = t_list[j]
                if j + 1 < len(t_list):
                    t_end = t_list[j + 1]
                else:
                    t_end = tmax  # Extend to the right edge

                # Skip if outside time range
                if t_end < tmin or t_start > tmax:
                    continue
                t_start = max(tmin, t_start)
                t_end = min(tmax, t_end)

                v = v_list[j]

                draw_top = True
                draw_bot = True
                draw_text = True
                fill_gray = False
                draw_vert = True
                if (v in {'x', 'X', 'z', 'Z'}):
                    draw_text = False
                    fill_gray = True
                if (si.two_level):
                    if v == '1':
                        draw_bot = False
                        draw_text = False
                    elif v == '0':
                        draw_top = False
                        draw_text = False
                    if vlast is not None:
                        if v == vlast:
                            draw_vert = False
                vlast = v
    
                # Draw a vertical line at the start of the segment                
                if draw_vert:
                    ax.vlines(t_start, ybot, ytop, color='black', linewidth=1)
                if draw_bot:
                    ax.hlines(ybot, t_start, t_end, color='black', linewidth=1)
                if draw_top:
                    ax.hlines(ytop, t_start, t_end, color='black', linewidth=1)

                # Fill gray for unknown values
                if fill_gray:
                    ax.fill_betweenx([ybot, ytop], t_start, t_end, color='lightgray')

                # Place text label in the middle of the segment
                # Check if there is enough space to draw the text
                if text_scale_factor <= 0:
                    draw_text = False
                if draw_text:
                    idx_start = ax.transData.transform((t_start, y))
                    idx_end = ax.transData.transform((t_end, y))

                    if idx_end[0] - idx_start[0] < len(v)*text_scale_factor:
                        draw_text = False
                if draw_text:
                    ax.text((t_start + t_end) / 2, y, v, ha='center', va='center',
                            fontsize=10, color='black')


        # Add clock grid lines if requested
        if add_clk_grid:
            clk_signal = None
            for s, si in self.sig_info.items():
                if si.is_clock:
                    clk_signal = si.name
                    break
            if not clk_signal:
                raise ValueError("No clock signal found in disp_signals for grid lines.")

            for i, t in enumerate(si.times):
                v = si.values[i]
                if v == '1':
                    ax.axvline(x=t, color='gray', linestyle='--', linewidth=0.5)

        ax.set_yticks([])
        ax.set_xlim(tmin - left_border, tmax + right_border)
        ax.set_ylim(0, ymax)


        return ax
    
    
    def extract_axis_bursts(
            self,
            clk_name : str,
            axis_sigs : dict[str, str]) -> list[dict]:
        """
        Extract bursts from AXI4-Stream signals.
        
        Parameters
        ----------
        clk_name: str
            Name of the clock signal.
        axis_sigs : dict[str, str]
            Dictionary of AXI4-Stream signal names with keys:
            'tdata', 'tvalid', 'tready', 'tlast'

        Returns
        -------
        bursts : list of dict
            Each dict has:
            - 'data': list of tdata values in the burst
            - 'start_idx': index of first beat in burst
            - 'beat_type':  list of status of each beat.
            beat_type[i] can be 0 (transfer, tvalid=tready=1), 1 (idle (tvalid=0)), 2 (stall (tready=0))
            - 'tstart': time of first beat in burst
        clk_period : float
            Estimated clock period in ns.
            Hence the time for beat i is tstart + i * clk_period
        """
        bursts = []
        current_burst = None

        # Extract clock times and resample AXI-Stream signals
        clk_sig = self.sig_info[clk_name]
        clk_times = extract_clock_times(clk_sig)
        tdata = resample_signal(self.sig_info[axis_sigs['tdata']], clk_times)
        tvalid = resample_signal(self.sig_info[axis_sigs['tvalid']], clk_times)
        tready = resample_signal(self.sig_info[axis_sigs['tready']], clk_times)
        tlast = resample_signal(self.sig_info[axis_sigs['tlast']]  , clk_times)

        for i in range(len(tdata)):
            # Handshake occurs only when both valid and ready are high
            if tvalid[i] and tready[i]:
                if current_burst is None:
                    # Start a new burst
                    current_burst = {
                        'data': [],
                        'start_idx': i,
                        'beat_type': [],
                        'tstart': clk_times[i]

                    }
                # Append this beat
                current_burst['data'].append(tdata[i])
                current_burst['beat_type'].append(0)  # transfer

                if tlast[i]:
                    # End of burst
                    current_burst['data'] = np.array(current_burst['data']).astype(np.uint32)
                    bursts.append(current_burst)
                    current_burst = None
            else:
                if current_burst is not None:
                    if not tvalid[i]:
                        current_burst['beat_type'].append(1)  # idle
                    elif not tready[i]:
                        current_burst['beat_type'].append(2)  # stall
                # Stall or idle → skip
                continue

        # Estimate clock period
        clk_diffs = np.diff(clk_times)
        clk_period = np.median(clk_diffs)

        return bursts, clk_period


def extract_clock_times(
        sig_info : SigInfo) -> list[float]:
    """
    Extracts the clock edge times from a VCD object for a given clock signal.

    Parameters
    ----------
    vcd : VCDVCD
        Parsed VCD object.
    clk_name : str
        Name of the clock signal.

    Returns
    -------
    clk_times : list of float
        List of times (in ns) when the clock signal transitions to '1'.
    """
    
    clk_times = []
    for t, v in zip(sig_info.times, sig_info.values):
        if v == '1':
            clk_times.append(t)  # Convert to ns

    clk_times = np.array(clk_times)

    return clk_times

def resample_signal(
        sig_info : SigInfo,
        clk_times : np.ndarray) -> np.ndarray:
    """
    Resamples a signal to new time points using nearest-neighbor interpolation.

    Parameters
    ----------
    sig_info : SigInfo
        Signal information object.
    new_times : np.ndarray
        Array of new time points to sample the signal at.  Typically these are clock edge times.

    Returns
    -------
    resampled_values : np.ndarray
        Array of signal values at the new time points.
    """    
    sig_times = sig_info.times
    sig_values = sig_info.numeric_values
    sampled = np.empty_like(clk_times, dtype=sig_values.dtype)

    j = 0  # pointer into sig_times and sig_values
    current_val = sig_values[0]

    for i, t_clk in enumerate(clk_times):
        # advance signal pointer while events are before or at this clock
        while j < len(sig_times) and sig_times[j] <= t_clk:
            current_val = sig_values[j]
            j += 1
        sampled[i] = current_val

    return sampled

