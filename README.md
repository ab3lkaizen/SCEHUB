# SCEWIN / AMISCE

AMISCE is a tool to modify BIOS NVRAM variables including options that are not visible through UEFI.

## Disclaimer

This project is NOT owned, supported or endorsed by [American Megatrends (AMI)](https://www.ami.com). Improper use could cause system instability. Use at your own risk.

## Solutions for various error messages

To determine the error message, attach the following argument to your command:

```bat
2> log-file.txt
```

A ``log-file.txt`` will be generated in the same directory as ``SCEWIN_64.exe`` is located, containing the error messages (if any).

The error codes can be divided into 3 categories:

1. [Both](#both)
2. [Export](#export)
3. [Import](#import)

## Both

### LoadDeviceDriver returned false | Error:1 Unable to load Driver | 10 - Error: Unable to load the driver

This error occurs:

1. When the drivers (originally named ``amifldrv64.sys`` and ``amigendrv64.sys``) is not in the same folder where ``SCEWIN_64.exe`` is located
2. The command wasn't run with admin privileges

To fix this error:

1. Be sure that the folder contains both ``amifldrv64.sys`` and ``amigendrv64.sys``
2. Be sure to run CMD with admin privileges

### ERROR:57 - Parsing CMD Line Arguments | ERROR:57 - Opening NVRAM Script File

This error occurs:

1. If the command used is incorrect or doesn't exist

To fix this error:

1. Verify that the command is correct
2. When importing, make sure that the NVRAM script file exists and has the same name as specified in the command

## Export

### WARNING: HII data does not have setup questions information

This error occurs:

1. When HII resources aren't getting published, therefore there is no data for the program to work with

To fix this error:

1. If you have an ASUS motherboard go [here](#asus)
2. I have not yet developed a solution for non-ASUS motherboards. It is currently being investigated

### ERROR:4 - Retrieving HII Database | ERROR:4 -  BIOS not compatible | ERROR:82 - Retrieving HII Database | ERROR:82 -  BIOS not compatible

This error occurs:

1. As the error message states, the BIOS may not be compatible. This can only happen if the BIOS is not from [AMI](https://en.wikipedia.org/wiki/American_Megatrends) therefore it won't work with any of AMI's tools

    - In order to check for BIOS manufacturer, paste the command below in CMD. If the vendor listed is "American Megatrends Inc." or "AMI" then you have an AMI BIOS

        ```bat
        systeminfo | findstr /I /C:BIOS
        ```

2. The ``SmiVariable`` is absent or outdated

    - Verify with [UEFITool](https://github.com/LongSoft/UEFITool) whether the module is absent or not

        - If it's absent, you can try [inserting](https://winraid.level1techs.com/t/guide-how-to-extract-insert-replace-efi-bios-modules-by-using-the-uefitool/32122) the module (obtain it from another BIOS, preferably from the same manufacturer)
        - If it's present, you can try [updating](https://winraid.level1techs.com/t/guide-how-to-extract-insert-replace-efi-bios-modules-by-using-the-uefitool/32122) the module (obtain it from another BIOS, preferably from the same manufacturer)

3. When using an outdated version of SCEWIN (e.g. version ``5.03.1115``) as newer motherboards only work with newer versions

### Platform identification failed

Platform identification depends on the ACPI module label (for Aptio V).

This error occurs:

1. When the Aptio core version is outdated. AMISCE requires Aptio core version 5.008+ for UEFI 2.3

To fix this error:

1. You may override this error with ``/d`` option as shown below

    ```bat
    SCEWIN_64.exe /O /S nvram.txt /d
    ```

## Import

### Warning: Error in writing variable \<variable\> to NVRAM

This error occurs:

1. The variable to be updated is write-protected
2. ``PCI Device`` has been disabled in Device Manager

To fix this error:

1. Enable ``PCI Device``s as follows:

    - Open Device Manager by typing ``devmgmt.msc`` in ``Win+R``
    - Navigate to ``Other devices``
    - Ensure that all ``PCI Device``s are enabled

2. If you have an ASUS motherboard (Z790+, B760+, H770+) go [here](#asus)

3. If you have an ASRock motherboard (Z590+, B560+, H510+) go [here](#asrock)

4. I have not yet developed a solution regarding variable write-protection for non-ASUS/ASRock motherboards. It is currently being investigated

### System configuration not modified

This error occurs:

1. You imported the NVRAM script file back unchanged, therefore SCEWIN didn't have to modify anything
2. SCEWIN was unable to apply the changes you made

   - This is related to the [previous error](#warning-error-in-writing-variable-variable-to-nvram)

### Warning in line \<xxxx\> | Missing Current Setting "*"

This error occurs:

1. When there is an error in the specified line number (indicated by the ``xxxx``)

To fix this error:

1. Comment out the setting or resolve the error manually

### Warning: Unmatched question... prompt: 'Setup Question', Token:' '

These two errors are related.

This error occurs:

1. When there is no value specified for ``token`` in the NVRAM script file (no \"\*" next to either option). The line specified in the error message is the same as the line of the last option in the ``Setup question``, whose token we just searched for.

    - See [media/error-message-example.png](/media/error-message-example.png)

To fix this error:

1. Put a "*" next to the value that ``BIOS Default`` suggests
2. You can use the ``/q`` option to suppress all warning messages as shown below. This warning message will not appear when importing, along with other (perhaps) useful ones

   ```bat
   SCEWIN_64.exe /I /S nvram.txt /q
   ```

### WARNING: Length of string for control '\<Setup Question\>' not updated as the value/defaults specified in the script file doesn't reach the minimum range (\<value\>)

This error occurs:

1. When the string given in the script is shorter than the minimum length specified in NVRAM external defaults (most likely). The usual cause for this is that the string has an initial empty value

> [!WARNING]
> Do NOT change the value of the string!

To fix this error:

1. You can use the ``/q`` option to suppress all warning messages. This warning message will not appear when importing, along with other (perhaps) useful ones

   ```bat
   SCEWIN_64.exe /I /S nvram.txt /q
   ```

2. Don't bother with it and leave it as is

### ASUS

If you have an ASUS motherboard (Z590+, B560+, H510+) follow the steps below.

1. Go to ``Setup > Tool`` section of your BIOS
2. Enable ``Publish HII Resources``

This way HII data will be published to the driver in which, SCEWIN should work flawlessly.

#### Z790+, B760+ Motherboards

This section is only required if you have a Z790+, B760+ motherboard. These motherboards require an additional workaround as they password protect the various runtime variables.

After following the above-mentioned steps, you need to disable ``Password protection of Runtime Variables``. In order to do so, follow the steps below.

1. Go to ``Setup > Advanced > UEFI Variables Protection`` section of your BIOS
2. Disable ``Password protection of Runtime Variables``

### ASRock

If you have an ASRock motherboard (Z590+, B560+, H510+) follow the steps below. These motherboards require an additional workaround as they password protect the various runtime variables.

1. Go to ``Setup > Advanced > UEFI Variables Protection`` section of your BIOS
2. Disable ``Password protection of Runtime Variables``

To access this setting, you need to mod your BIOS with [UEFI Editor](https://boringboredom.github.io/UEFI-Editor). ASRock's BIOS has 2 Advanced forms so you need to do a [Menu swap](https://github.com/BoringBoredom/UEFI-Editor#menu) in order to gain access to the setting.

## Issues

Additional error messages or possible non-working solutions should be reported in the [issue tracker](https://github.com/ab3lkaizen/SCEWIN-fixes/issues).

Complete the appropriate issue template. Consider whether your problem is covered by an existing issue; if so, follow the discussion there. Avoid commenting on existing recurring issues, as such comments do not contribute to the discussion of the issue and may be treated as spam.
