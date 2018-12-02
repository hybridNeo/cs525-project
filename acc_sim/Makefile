CC=g++
CFLAGS=-I. -pthread
DEPS = acc-simulator.h
OBJ = acc-simulator.cpp main.cpp

%.o: %.cpp $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

simulator: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

clean:
	rm *.o simulator
