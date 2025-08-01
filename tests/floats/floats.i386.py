import logging
import struct
import sys

import smallworld

# Set up logging and hinting
smallworld.logging.setup_logging(level=logging.INFO)
smallworld.hinting.setup_hinting(stream=True, verbose=True)

# Define the platform
platform = smallworld.platforms.Platform(
    smallworld.platforms.Architecture.X86_32, smallworld.platforms.Byteorder.LITTLE
)

# Create a machine
machine = smallworld.state.Machine()

# Create a CPU
cpu = smallworld.state.cpus.CPU.for_platform(platform)
machine.add(cpu)

# Load and add code into the state
code = smallworld.state.memory.code.Executable.from_filepath(
    __file__.replace(".py", ".bin")
    .replace(".angr", "")
    .replace(".panda", "")
    .replace(".pcode", ""),
    address=0x1000,
)
machine.add(code)

# Set the instruction pointer to the code entrypoint
cpu.eip.set(code.address)

# Initialize argument registers
arg1 = int.from_bytes(struct.pack("d", float(sys.argv[1])), "little")
arg2 = int.from_bytes(struct.pack("d", float(sys.argv[2])), "little")

cpu.xmm0.set(arg1)
cpu.xmm1.set(arg2)

# Emulate
emulator = smallworld.emulators.UnicornEmulator(platform)
emulator.add_exit_point(cpu.eip.get() + code.get_capacity())
final_machine = machine.emulate(emulator)

# read out the final state
cpu = final_machine.get_cpu()
raw = cpu.xmm0.get()
(res,) = struct.unpack("d", raw.to_bytes(8, "little"))
print(f"{res}")
