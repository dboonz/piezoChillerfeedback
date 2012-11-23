#Acq_IncClk.py
# This is a near-verbatim translation of the example program
# C:\Program Files\National Instruments\NI-DAQ\Examples\DAQmx ANSI C\Analog In\Measure Voltage\Acq-Int Clk\Acq-IntClk.c

# 2011.12.19 - try implementation reading from two channels (Jonas)

import ctypes
import numpy
import time
nidaq = ctypes.windll.nicaiu # load the DLL

plt.ion()


##############################
# Setup some typedefs and constants
# to correspond with values in
# C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h
# the typedefs
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32

# the constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_RSE = 10083
DAQmx_Val_diff = 10106
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0
##############################


def CHK(err):
    """a simple error checking routine"""
    if err < 0:
        buf_size = 100
        buf = ctypes.create_string_buffer('\000' * buf_size)
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))



# Initialize an analog input channel for voltage measurement
def init_channel(taskHandle, nr_samples, clockspeed = 10000.0):
    max_num_samples = nr_samples
    data = numpy.zeros((max_num_samples,),dtype=numpy.float64)

    # Send commands to initialize an analog input channel
    CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))
    CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai0","",
                                       DAQmx_Val_diff,  ###
                                       float64(-10.0),float64(10.0),
                                       DAQmx_Val_Volts,None))

    CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(clockspeed),
                                    DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                    uInt64(max_num_samples)));
    return data

# Initialize an analog input channel for voltage measurement
def init_channel2(taskHandle, nr_samples, clockspeed = 10000.0):
    max_num_samples = nr_samples
    data = numpy.zeros((max_num_samples,),dtype=numpy.float64)

    # Send commands to initialize an analog input channel
    CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))
    CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai2","",
                                       DAQmx_Val_diff,  ###
                                       float64(-10.0),float64(10.0),
                                       DAQmx_Val_Volts,None))

    CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(clockspeed),
                                    DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                    uInt64(max_num_samples)));
    return data



# Read an array of voltage data points from the channel
def read_voltage(taskHandle, nr_samples, data, read):
    max_num_samples = nr_samples
    CHK(nidaq.DAQmxStartTask(taskHandle))
    CHK(nidaq.DAQmxReadAnalogF64(taskHandle,max_num_samples,float64(10.0),
                                 DAQmx_Val_GroupByChannel,data.ctypes.data,
                                 max_num_samples,ctypes.byref(read),None))
    nidaq.DAQmxStopTask(taskHandle)
    return data



if __name__ == "__main__":

  #import pylab
  import matplotlib
  matplotlib.use('TkAgg')
  import matplotlib.pyplot as plt
  fig = plt.figure()
  read = int32()
  taskHandle = TaskHandle(0)
  nr_samples = 10
  data = init_channel(taskHandle,nr_samples,10000.0)

  points = []
  time_axis = []

  ax = fig.add_subplot(111)
  line, = ax.plot([], [])
  ax.set_ylim(-1.1, 1.1)
  ax.set_xlim(0, 5)

  #image, = pylab.plot(x,points)

  start = time.time()
  for i in range(30):
      data = read_voltage(taskHandle, nr_samples, data, read)
      points.append(numpy.average(data))
      time_axis.append(i)
      
      line.set_data(time_axis,points)
      ax.set_xlim(0,30)
      ax.set_ylim(0,10)
      #ax.set_xlim(0,i+1.0)
      #ax.set_ylim(min(points),max(points))
      ax.figure.canvas.draw()
      time.sleep(.01)
      


  print (time.time()-start)/100.0
  print "Acquired %d points"%(read.value)



  if taskHandle.value != 0:
      nidaq.DAQmxStopTask(taskHandle)
      nidaq.DAQmxClearTask(taskHandle)


  print numpy.average(data)

