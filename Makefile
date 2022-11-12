# If the first argument is "run"...
ifeq (run,$(firstword $(MAKECMDGOALS)))
    # use the rest as arguments for "run"
    ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
    # ...and turn them into do-nothing targets
    $(eval $(ARGS):;@:)
endif

filename=$(word 1,$(ARGS))




.PHONY:
run: filename
	@python3 CompiloVVS.py $(word 1, $(ARGS))
	@nasm -f elf64 ouf.asm
	@gcc -no-pie -fno-pie ouf.o
	./a.out $(filter-out $(word 1,$(ARGS)), $(ARGS))

filename: