# -*- coding: utf-8 -*-
"""CP2000 constants."""

REG_2000_REV_DIRECTION = True

# CP2000 registers CP2000_UM_EN_20170602 page 453
REG_2000 =           0x2000
REG_2000_F_NO =      0b00000000
REG_2000_F_STOP =    0b00000001
REG_2000_F_RUN =     0b00000010
REG_2000_F_JOG =     0b00000011

REG_2000_F_NOF =     0b00000000
REG_2000_F_FWD =     0b00010000
REG_2000_F_REV =     0b00100000
REG_2000_F_CHDIR =   0b00110000

REG_2000_F_ACDEC1 =  0b00000000
REG_2000_F_ACDEC2 =  0b01000000
REG_2000_F_ACDEC3 =  0b10000000
REG_2000_F_ACDEC4 =  0b11000000
REG_2000_F_STEPMASK =   0b1111 << 8
REG_2000_F_EN0611 =     0b1 << 12
REG_2000_F_DKEYPAD =    0b01 << 13
REG_2000_F_SET0021 =    0b10 << 13
REG_2000_F_CHOPSOURCE = 0b11 << 13

REG_FREQUENCY = 0x2001  # XXX.XX Hz

REG_2002 = 0x2002
REG_2002_F_EXTFAULT = 0b000
REG_2002_F_RESET =    0b010
REG_2002_F_PAUSEON =  0b100

# State registers. (Read only)
REG_ERROR = 0x2100  # High byte: Warn Code, Low Byte: Error Code

REG_STATE = 0x2101
REG_STATE_F_STOP =       0b00  # Стоп
REG_STATE_F_DECEL =      0b01  # Замедление
REG_STATE_F_SANDBY =     0b10  # Готовность
REG_STATE_F_OPERATING =  0b11  # Работа
REG_STATE_F_JOGCOMMAND = 0b100  # JOG Command
REG_STATE_F_RWDRUN =     0b00000
REG_STATE_F_REVTORWD =   0b01000
REG_STATE_F_REVRUN =     0b10000
REG_STATE_F_FWDTOREV =   0b11000
REG_STATE_F_COMINTFREQ =  1 << 8
REG_STATE_F_ANSIGFREQ =   1 << 9
REG_STATE_F_COMINTOPCOM = 1 << 10
REG_STATE_F_PARLOC =      1 << 11
REG_STATE_F_COPYKEYPAD =  1 << 12

REG_FREQUENCY_COMMAND =  0x2102  # XXX.XX Hz
REG_FREQUENCY_OUTPUT =   0x2103  # XXX.XX Hz
REG_OUTPUT_CURRENT =     0x2104  # XXX.XX A
REG_DCBUS_Voltage =      0x2105  # XXX.X V
REG_Output_Voltage =     0x2106  # XXX.X V
REG_Current_Step =       0x2107
REG_Counter_Value =      0x2109
REG_Power_Factor_Angle = 0x210A  # XXX.X
REG_Output_Torque =      0x210B  # XXX.X%
REG_Actual_Motor_Speed = 0x210C  # XXXXXrpm
REG_Power_Output =       0x210F  # X.XXX KWH
REG_Multi_function_display = 0x2116  # Pr.00-04
REG_Max_Operation_Value =    0x211B
REG_Decimal_Current_Value =  0x211F  # display
REG_Display_Output_Current = 0x2200  # XXX.XA

REG_Display_Counter_Value = 0x2201  # c
REG_Actual_Output_Frequency = 0x2202  # XXXXXHz
REG_DC_BUS_Voltage = 0x2203  # XXX.XV
REG_Output_Coltage = 0x2204  # XXX.XV
REG_Power_Angle = 0x2205  # XXX.X
REG_Display_Actual_Motor_Speed = 0x2206  # XXXXXkW

REG_Motor_Speed = 0x2207  # XXXXXrpm
REG_Output_Torque = 0x2208  # XXX.X%
REG_PID_Feedback = 0x220A  # XXX.XX%
REG_AVI_Analog_input_Terminal1 = 0x220B
REG_AVI_Analog_input_Terminal2 = 0x220C
REG_AVI_Analog_input_Terminal3 = 0x220D
REG_Temperature_Drive_Power_Module = 0x220E  # XXX.X℃
REG_Temperature_Capacitance = 0x220F  # XXX.X℃
REG_Digital_Input_Status0212 = 0x2210  # ON/OFF
REG_Digital_Input_Status0218 = 0x2211  # ON/OFF
REG_MultiStepDpeed = 0x2212  # S
REG_CPU_pin_status00043 = 0x2213
REG_CPU_pin_status00044 = 0x2214
REG_Times_Counter_Overload = 0x2219  # XXX.XX%
REG_GFF = 0x221A  # XXX.XX%
REG_DCbus_Voltage_Ripples = 0x221B  # XXX.XV
REG_PLC_register_D1043 = 0x221C  # C
REG_User_page_displays = 0x221E
REG_Output_Value0005 = 0x221F  # XXX.XXHz
REG_Number_Revolutions = 0x2220
REG_Motor_Running_Position = 0x2221
REG_Fan_Speed = 0x2222  # XXX%
REG_Control_Mode = 0x2223  # 0: speed mode, 1: torque mode
REG_Carrier_Frequency = 0x2224  # XXKHZ
REG_Drive_Status = 0x2226
REG_Drive_Status_NoDirection = 0b00
REG_Drive_Status_Forward =     0b01
REG_Drive_Status_Reverse =     0b10
REG_Drive_Status_Ready =     0b0100
REG_Drive_Status_Error =     0b1000
REG_Drive_Status_Output =   0b10000  # 1 did output, 0 did not output
REG_Drive_Status_Alarm =   0b100000  # 0 no alarm, 1 have alarm
REG_Drive_estimated_output = 0x2227  # XXXX Nt-m
REG_KWH_display =   0x2229  # XXXX.X
REG_PID_Reference = 0x222E  # XXX.XX%
REG_PID_Offset =    0x222F  # XXX.XX%
REG_PID_Output_Frequency = 0x2230  # XXX.XXHz
REG_Hardware_ID = 0x2231


RegDesctriptions = [
["REG_ERROR", "", ""],
["REG_STATE", "", ""],
["REG_FREQUENCY_COMMAND", "XXX.XX Hz", ""],
["REG_FREQUENCY_OUTPUT", "XXX.XX Hz", ""],
["REG_OUTPUT_CURRENT", "XXX.XX A", ""],
["REG_DCBUS_Voltage", "XXX.X V", ""],
["REG_Output_Voltage", "XXX.X V", ""],
["REG_Current_Step", "", ""],
["REG_Counter_Value", "", ""],
["REG_Power_Factor_Angle", "XXX.X", ""],
["REG_Output_Torque", "XXX.X%", ""],
["REG_Actual_Motor_Speed", "XXXXXrpm", ""],
["REG_Power_Output", "X.XXX KWH", ""],
["REG_Multi_function_display", "", ""],
["REG_Max_Operation_Value", "", ""],
["REG_Decimal_Current_Value", "", ""],
["REG_Display_Output_Current", "XXX.XA", ""],
["REG_Display_Counter_Value", "c", ""],
["REG_Actual_Output_Frequency", "XXXXXHz", ""],
["REG_DC_BUS_Voltage", "XXX.XV", ""],
["REG_Output_Coltage", "XXX.XV", ""],
["REG_Power_Angle", "XXX.X", ""],
["REG_Display_Actual_Motor_Speed", "XXXXXkW", ""],
["REG_Motor_Speed", "XXXXXrpm", ""],
["REG_Output_Torque", "XXX.X%", ""],
["REG_PID_Feedback", "XXX.XX%", ""],
["REG_AVI_Analog_input_Terminal1", "", ""],
["REG_AVI_Analog_input_Terminal2", "", ""],
["REG_AVI_Analog_input_Terminal3", "", ""],
["REG_Temperature_Drive_Power_Module", "XXX.X℃", ""],
["REG_Temperature_Capacitance", "XXX.X℃", ""],
["REG_Digital_Input_Status0212", "ON/OFF", ""],
["REG_Digital_Input_Status0218", "ON/OFF", ""],
["REG_MultiStepDpeed", "S", ""],
["REG_CPU_pin_status00043", "", ""],
["REG_CPU_pin_status00044", "", ""],
["REG_Times_Counter_Overload", "XXX.XX%", ""],
["REG_GFF", "XXX.XX%", ""],
["REG_DCbus_Voltage_Ripples", "XXX.XV", ""],
["REG_PLC_register_D1043", "C", ""],
["REG_User_page_displays", "", ""],
["REG_Output_Value0005", "XXX.XXHz", ""],
["REG_Number_Revolutions", "", ""],
["REG_Motor_Running_Position", "", ""],
["REG_Fan_Speed", "XXX%", ""],
["REG_Control_Mode", "", ""],
["REG_Carrier_Frequency", "XXKHZ", ""],
["REG_Drive_Status", "", ""],
["REG_Drive_estimated_output", "XXXX Nt-m", ""],
["REG_KWH_display", "XXXX.X", ""],
["REG_PID_Reference", "XXX.XX%", ""],
["REG_PID_Offset", "XXX.XX%", ""],
["REG_PID_Output_Frequency", "XXX.XXHz", ""],
["REG_Hardware_ID", "", ""]
]
