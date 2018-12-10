CC=g++ -std=c++11
CFLAGS=-I. -pthread
DEPS = acc-simulator.h
OBJ = acc-simulator.cpp main.cpp

%.o: %.cpp $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

simulator: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

clean:
	rm -f *.o simulator
