CXX=g++
CXXFLAGS = -c -Wall
DEPS = gpu-simulator.h 

all: gpu-simulator.o 

%.o: %.cpp $(DEPS)
	$(CXX) -o $@ $< $(CXXFLAGS)

