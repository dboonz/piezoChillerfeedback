 # -*- coding: utf-8 -*-
from __future__ import with_statement
import matplotlib
matplotlib.use('TkAgg')


import serialChiller 
try :
  from read_AI_signal_daqmx import *
except :
  print "Probably on linux. NIDAQ won't work"

import time


import numpy as np
from Tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

### comb
PIEZO_VOLTAGE_MAX = 10 # could be 7, TODO
# voltages are -1 to 6
# offset = 2.6
chiller_serialport = 3
                


class Application(Frame):

        def __init__(self,master = None):
                Frame.__init__(self,master)
                self.pack()
                self.master = master
                self.mainframe = self
                print 'serial chiller'
                self.createWidgets()

        def createWidgets(self):
            """ Creates the widgets for this application """
            " Top frame "
            self.firstF = Frame(self.mainframe,bd=2, relief = RIDGE)
            self.firstF.grid()

            " Frame for device "
            self.device1 = LabelFrame(self.mainframe,bd=2, relief = RIDGE)#, text = 'Temp. feedback rep.rate')
            self.device1.grid(row = 1, column = 0)#, columnspan = 4)                

            " Chiller feedback frame"
            self.chillerFeedback_LF = LabelFrame(self.mainframe,bd=2, relief = RIDGE, text = 'PUMP: Temp. feedback rep.rate')
            self.chillerFeedback_LF.grid(row = 2, column = 0)#, columnspan = 4)
           
            self.save_LF = LabelFrame(self.mainframe,bd=2, relief = RIDGE)#, text = 'fit')
            self.save_LF.grid(row = 4, column = 0)#, columnspan = 4)
            
            " Create the variables for the application "
            self.stopLoop = IntVar()
            self.stopLoop.set(0)
            
            self.LastDataSaved = IntVar()
            self.LastDataSaved.set(0)
            
            self.devices_initialised = IntVar()
            self.devices_initialised.set(0)
            
            self.deviationVoltage_DG= DoubleVar()
            self.deviationVoltage_DG.set(0.05)
            
            " Startbutton with 'gumbo'"
            self.startB = Button(self.firstF, text = 'gumbo', command = self.mainLoop)
            self.startB.pack(side = LEFT)
            
            " Checkbox for stopping "
            self.stopLoopCB = Checkbutton(self.firstF, text = 'halt', variable = self.stopLoop)
            self.stopLoopCB.pack(side = LEFT, padx = 10)
            
            self.deleteDataB = Button(self.firstF, text = 'delete Data', command = self.deleteData)
            self.deleteDataB.pack(side = LEFT)

            self.testB = Button(self.firstF, text = 're-read set temp', command = self.test)
            self.testB.pack(side = LEFT)
            
            
            self.deviationVoltage_DGE= Entry(self.firstF, textvariable=self.deviationVoltage_DG, bg='white', width = 11)
            self.deviationVoltage_DGE.pack(side = LEFT)

            
            self.ShutdownAndQuitB = Button(self.firstF, text = "Quit", command = self.Quit)
            self.ShutdownAndQuitB.pack(side = RIGHT)
            

            self.k = number_dataArrays = 2
            self.k = number_dataArrays = 2 # Don't know what it does, but
                                            # probably it should be one if there's only one monitoring
            
            self.dat = []
            for a in range(self.k):
                    self.dat.append([])
            
            self.t = []
            
            self.font_label=('Helvetica', 20, 'bold')
            self.font_entry = ('Helvetica', 30, 'bold')
                
            self.sleep_time_per_meas = DoubleVar()
            self.sleep_time_per_meas.set(500)
            
            self.limit_plot_y_axis = IntVar()
            self.limit_plot_y_axis.set(0)
            
            self.y1lim = DoubleVar()
            self.y1lim.set(0.9)
            
            self.y2lim = DoubleVar()
            self.y2lim.set(1.1)

            
            self.sets_to_plot = IntVar()
            self.sets_to_plot.set(500)
            
    
            self.filename = StringVar()
            self.filename.set('temp.txt')

            Label(self.device1, text = "sleep time [ms]").pack(side = LEFT)
            self.sleep_time_per_measE= Entry(self.device1, textvariable=self.sleep_time_per_meas, bg='white', width = 5)
            self.sleep_time_per_measE.pack(side = LEFT)

            self.stopLoopCB = Checkbutton(self.device1, text = 'ylims', variable = self.limit_plot_y_axis)
            self.stopLoopCB.pack(side = LEFT, padx = 10)

            self.y1E= Entry(self.device1, textvariable=self.y1lim, bg='white', width = 5)
            self.y1E.pack(side = LEFT)
            
            self.y2E= Entry(self.device1, textvariable=self.y2lim, bg='white', width = 5)
            self.y2E.pack(side = LEFT)
            
            Label(self.save_LF, text = "sets to plot:").pack(side = LEFT)
            self.sets_to_plotE= Entry(self.save_LF, textvariable=self.sets_to_plot, bg='white', width = 5)
            self.sets_to_plotE.pack(side = LEFT)

            self.saveB = Button(self.save_LF, text = "save", command = self.save)
            self.saveB.pack(side = LEFT)
            
            self.filenameE= Entry(self.save_LF, textvariable=self.filename, bg='white', width = 50)
            self.filenameE.pack(side = LEFT)
            
            
            ### self.chillerFeedback_LF
            self.T_set = IntVar()
            self.T_set.set(0)
            self.T_min = IntVar()
            self.T_min.set(221)
            self.T_max = IntVar()
            self.T_max.set(233)
            self.Vpi_lim_low = DoubleVar()
            self.Vpi_lim_low.set(0.3*PIEZO_VOLTAGE_MAX)
            self.Vpi_lim_high = DoubleVar()
            self.Vpi_lim_high.set(0.7*PIEZO_VOLTAGE_MAX)
            self.T_delta_t = DoubleVar()
            self.T_delta_t.set(30)
            self.T_feedback = IntVar()
            self.T_feedback.set(0)
            
            self.counter_T_feedback = 0.
            self.counter_T_feedback_reset_bool = 1
            
            Label(self.chillerFeedback_LF, text = "T_set").pack(side = LEFT)
            self.T_setE= Entry(self.chillerFeedback_LF, textvariable=self.T_set, bg='white', width = 5)
            self.T_setE.pack(side = LEFT)

            Label(self.chillerFeedback_LF, text = "T_min").pack(side = LEFT)
            self.T_minE= Entry(self.chillerFeedback_LF, textvariable=self.T_min, bg='white', width = 5)
            self.T_minE.pack(side = LEFT)

            Label(self.chillerFeedback_LF, text = "T_max").pack(side = LEFT)
            self.T_maxE= Entry(self.chillerFeedback_LF, textvariable=self.T_max, bg='white', width = 5)
            self.T_maxE.pack(side = LEFT)

            Label(self.chillerFeedback_LF, text = "Vpi_lim_low").pack(side = LEFT)
            self.Vpi_lim_lowE= Entry(self.chillerFeedback_LF, textvariable=self.Vpi_lim_low, bg='white', width = 5)
            self.Vpi_lim_lowE.pack(side = LEFT)

            Label(self.chillerFeedback_LF, text = "Vpi_lim_high").pack(side = LEFT)
            self.Vpi_lim_highE= Entry(self.chillerFeedback_LF, textvariable=self.Vpi_lim_high, bg='white', width = 5)
            self.Vpi_lim_highE.pack(side = LEFT)

            Label(self.chillerFeedback_LF, text = "T_delta_t").pack(side = LEFT)
            self.T_delta_tE= Entry(self.chillerFeedback_LF, textvariable=self.T_delta_t, bg='white', width = 5)
            self.T_delta_tE.pack(side = LEFT)
            
            self.T_feedbackCB = Checkbutton(self.chillerFeedback_LF, text = 'lock', variable = self.T_feedback)
            self.T_feedbackCB.pack(side = LEFT, padx = 10)
            
            ### for matplotlib
            self.fig = plt.figure(figsize = (5,3))
            self.canvas = FigureCanvasTkAgg(self.fig, master=root)
            self.toolbar = NavigationToolbar2TkAgg( self.canvas, root )
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)#grid(row = 0, column = 2)#
            
            self.ax = plt.subplot(111)
            self.ax.set_ylabel('signal [V]')
            self.ax.set_xlabel('t [s]')              
            self.ax.plot([1,4,2])
            self.canvas.draw()

               

                
        def initSerialToChiller_and_NI_daqmx(self):

                attemps_connect_to_chiller = 0
                while attemps_connect_to_chiller < 3:
                        try :
                                self.ser = serialChiller.open_chiller_port(chiller_serialport)
                                print 'establised connection with the ', attemps_connect_to_chiller, ' attemp' 
##                                status = readChillerStatus(serialPort = self.ser)
                                realtemp = serialChiller.readCoolantTemperature(serialPort = self.ser)
##                                settemp = readSetTemperature(serialPort = self.ser)
####                                print 'status',status
                                print 'actual temp',realtemp
##                                print 'set temp.',settemp
                                self.T_set.set(serialChiller.readSetTemperature(self.ser))

                                time.sleep(0.3)
                                break
                        except :
                                attemps_connect_to_chiller += 1
                                time.sleep(0.5)
                                print 'not attemp', attemps_connect_to_chiller
                                pass
                
                
                
               

                print 'yeay'
                
                
                self.read = int32()
                self.taskHandle = TaskHandle(0)
                self.taskHandle_b = TaskHandle(1)
                self.nr_samples = 10
                
                self.data = init_channel(self.taskHandle,self.nr_samples,10000.0)
                
                print 'devices initialised'
                
                self.devices_initialised.set(1)

                
                
        
        def deleteData(self):
                self.t = []
                for i in range(self.k):
                        self.dat[i] = []
        
        def read_data_NI_daqmx(self):
                
                data = read_voltage(self.taskHandle, self.nr_samples, self.data, self.read)
                for i in range(self.k):
                     #   print "Measured something:", numpy.average(self.data)
                        self.dat[i].append(numpy.average(self.data))
        
        def feedback_T(self):
                #xxx
                #print 'start'
                if self.counter_T_feedback_reset_bool == 1:
                        self.counter_T_feedback = self.t[-1]
                        self.counter_T_feedback_reset_bool = 0
                else:
                        if (self.t[-1] - self.counter_T_feedback) > self.T_delta_t.get(): # so every self.T_delta_t seconds
                                
                                self.counter_T_feedback_reset_bool = 1
                                
                                try:
                                        last_piezo_voltage = np.mean(self.dat[0][-5:]) # tries to average over the last 5 temperature values if possible
                                except:
                                        last_piezo_voltage = self.dat[0][-1] # takes last value of data array of the index corresponding to the name piezo_voltage
                                
                                if last_piezo_voltage < 0.05:
                                        print 'last piezo voltage was smaller 0.05 V, piezo feedback close?'
                                else:
                                
                                        change_temperature = 0
                                        
                                        if last_piezo_voltage > self.Vpi_lim_high.get():
                                                new_set_temp = self.T_set.get() - 1
                                                if new_set_temp > self.T_min.get():
                                                        self.T_set.set(new_set_temp)
                                                        change_temperature = 1
                                                else:
                                                        print 'Temp feedback reached higher specified limit'
                                        
                                        if last_piezo_voltage < self.Vpi_lim_low.get():
                                                new_set_temp = self.T_set.get() + 1
                                                if new_set_temp < self.T_max.get():
                                                        self.T_set.set(new_set_temp)
                                                        change_temperature = 1
                                                else:
                                                        print 'Temp feedback reached lower specified limit'
                                                
                                        if change_temperature == 1:
                                                time.sleep(0.3)
                                                try:
                                                        changedTemperature = serialChiller.setTemperature(serialPort = self.ser, temp = self.T_set.get())
                                                        print 'CHANGED baseplate temperature at t = ',round(self.t[-1]), ' s  to  ', new_set_temp
                                                except:
                                                        print 'WARNING - could not CHANGE the set temperature at t = ',self.t[-1]
                                                
                                                if changedTemperature != -1 and changedTemperature > self.T_min.get() and changedTemperature < self.T_max.get():
                                                        self.T_set.set(changedTemperature)
                                                else: # in case just the reply from the changed temperature hanged, we ask for the temperature one more time manually
##                                                        try:
##                                                                changedTemperature = readSetTemperature(self.ser)
##                                                        except:
##                                                                print 'WARNING - could not manually READ the set temperature at t = ',self.t[-1]
                                                        if changedTemperature != -1 and changedTemperature > self.T_min.get() and changedTemperature < self.T_max.get() :
                                                                self.T_set.set(changedTemperature)
                                                                print 'determined changed baseplate by manually asking, instead of the reply from serial_Chiller255p.setTemperature' 
                                                                
                                                        
                                                #time.sleep(0.3)
                                                #serial_Chiller255p.readChillerStatus(serialPort = self.serialPort_S0_chiller)
                                                
                                                #print 'tried to change chiller temperatur'
                                        print 'checked baseplate temperature at t = ',round(self.t[-1]), ' s'
                                
                                
       
        def mainLoop(self):
                
                if not self.devices_initialised.get():
                        self.initSerialToChiller_and_NI_daqmx()
                        print 'serialToChiller set up'
                
                self.stopLoop.set(0)
                
                if len(self.t) > 1:
                        self.t0 =  time.time() - self.t[-1]
                else:
                        self.t0 = time.time()
                

                while self.stopLoop.get() != 1:
                  #print "in main-while-loop"
                  #print "Reading NI"
                  self.read_data_NI_daqmx()
                  #print "updating plots"
                  self.update_plots()
                  if self.T_feedback.get():
                    self.feedback_T()
                  root.update()
                  time.sleep(self.sleep_time_per_meas.get()/1000.)

        
        def update_plots(self):
          #print "In update_plots"
          self.t.append(time.time() - self.t0)

          ### PLOTTING
          self.ax.clear()
          ### updates the plots for the last n_sets_to_plot data aquisitions. x axis divided by 28 to come to seconds instead of shots
          n_sets_to_plot = self.sets_to_plot.get()
          #print 'n_sets_to_plot: %d' % n_sets_to_plot
          n_sets_to_plot = min(n_sets_to_plot, len(self.t))
          if n_sets_to_plot <1:
                  n_sets_to_plot = 1


#          
#          # makes sure that if there are fewer sets than selected for plotting (e.g. at the very beginning, that only this fewer sets are plotted
#          if len(self.dat[i]) < n_sets_to_plot + 1:
#            print "Nothing to plot"
#            n_sets_to_plot = 0
#          
          
          self.ax.plot(self.t[-n_sets_to_plot:], np.array(self.dat[0][-n_sets_to_plot:]), label = 'pi pump')
  
          
          plt.legend(loc = 'lower left')
          if self.limit_plot_y_axis.get():
                  plt.ylim( self.y1lim.get(), self.y2lim.get() )
          self.fig.canvas.draw()

                
        def test(self):
##                self.ser = open_chiller_port(3)
##                status = readChillerStatus(serialPort = self.ser)
##                realtemp = readCoolantTemperature(serialPort = self.ser)
##                settemp = readSetTemperature(serialPort = self.ser)
                self.T_set.set(serialChiller.readSetTemperature(self.ser))
                self.T_set_b.set(serialChiller.readSetTemperature(self.ser_b))
##                print 'status',status
##                print 'actual temp',realtemp
##                print 'set temp.',settemp
                print 'aua'
        
        
        def save(self): 


                grouped_columns = [self.t]
                for i in range(self.k):
                        grouped_columns.append(self.dat[i])
                combined_data = np.column_stack((grouped_columns))
                filename = self.filename.get()
                for i in range(self.k):
                        filename +'_'+device_names[i]
                np.savetxt(filename,combined_data)
                
                print 'data saved to',filename
                
                
        def Quit(self):

                try:
                        serialChiller.close_chiller_port(self.ser)
                except:
                       print 'could not close serial connection' 
                
                try:
                        serialChiller.close_chiller_port(self.ser_b)
                except:
                       print 'COmB: could not close serial connection' 
                
                try:
                        if self.taskHandle.value != 0:
                            nidaq.DAQmxStopTask(self.taskHandle)
                            nidaq.DAQmxClearTask(self.taskHandle)
                except:
                        print 'could not close connection to NI device'
                plt.close('all')
                self.master.quit()


if __name__ == '__main__':
  root = Tk()

  root.title("Chiller feedback for Piezo")
  app = Application(root)
  root.mainloop()

  root.destroy()
