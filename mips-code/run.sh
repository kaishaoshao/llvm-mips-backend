pushd mips-code
llvm-mc --arch=mips test_qemu.asm -filetype=obj -o build/test.o
mips-linux-gnu-ld -static build/test.o -o build/test
qemu-mips-static build/test
popd


exit
mips-linux-gnu-gcc hello-mips.o -o hello-mips -static
mips-linux-gnu-as hello-mips-llc.s -o hello-mips-llc.o
mips-linux-gnu-gcc hello-mips-llc.o -o hello-mips-llc -static
qemu-mips-static hello-mips-llc