set unroll_factors {1 2 4 8}

foreach uf $unroll_factors {
    set sol_name "sol_uf$uf"
    open_project vmult_hls -reset
    set_top vec_mult

    # Pass UNROLL_FACTOR as a macro
    add_files -cflags "-Iinclude -DPIPELINE_EN=1 -DUNROLL_FACTOR=$uf" src/vmult.cpp
    add_files -tb testbench/tb_vmult.cpp

    open_solution $sol_name -reset
    set_part {xczu48dr-ffvg1517-2-e}
    create_clock -period 3.33 -name default

    # Optional: run C simulation
    # csim_design

    csynth_design

    # Optional: run co-simulation
    # cosim_design

    # Optional: export IP
    # export_design -format ip_catalog

    # Construct full path to the XML report
    set report_path "vmult_hls/$sol_name/syn/report/vec_mult_Pipeline_mult_loop_csynth.xml"

    # Construct rclone copy command
    set rclone_cmd "cp  $report_path ./vmult_reports/mult_loop_csynth_uf$uf.xml"

    # Execute the shell command
    exec sh -c $rclone_cmd

    # Save and close the project
    close_project

}

exit