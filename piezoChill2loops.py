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
import logging
logging.basicConfig(level=logging.DEBUG)

chiller_serialport = 3

class Application(Frame):
            #  initial settings for the parameters
        tmax = 233
        tmin = 180
        piezo_voltage_max = 6
        piezo_voltage_min = -1
        t_delta_t = 30
        offset_voltage = 2.55 # Offset voltage for the loop
        max_std_voltage_in_lock = 0.02 #  maximum standard deviation before
        # out of lock is assumed


        def __init__(self,master = None):
            self.logger = logging.getLogger('Baseplate')
            Frame.__init__(self,master)
            master.protocol("WM_DELETE_WINDOW",self.Quit)
            self.pack()
            self.master = master
            self.mainframe = self
            print 'serial chiller'
            self.createWidgets()

        def test(self):
            self.T_set.set(serialChiller.readSetTemperature(self.ser))

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

            # 'record wether the last temperature change was up or down'
            self.lastTemperatureChange = 'None' 
            self.temperature_data = [] #  last temperature data
           
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
            self.y1lim.set(self.piezo_voltage_min)
           
            self.y2lim = DoubleVar()
            self.y2lim.set(self.piezo_voltage_max)

           
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
            self.T_min.set(self.tmin)
            self.T_max = IntVar()
            self.T_max.set(self.tmax)
            voltage_range = self.piezo_voltage_max - self.piezo_voltage_min
            self.Vpi_lim_low = DoubleVar()

            self.Vpi_lim_low.set(self.piezo_voltage_min + 0.2*voltage_range)
            self.Vpi_lim_high = DoubleVar()
            self.Vpi_lim_high.set(self.piezo_voltage_max - 0.2*voltage_range)
            self.T_delta_t = DoubleVar()
            self.T_delta_t.set(self.t_delta_t)
            self.T_feedback = IntVar()
            self.T_feedback.set(0)
           
            self.counter_T_feedback = 0.
            self.counter_T_feedback_reset_bool = 1

            self.T_feedbackCB = Checkbutton(self.chillerFeedback_LF, text = 'lock', variable = self.T_feedback)
            self.T_feedbackCB.pack(side = LEFT, padx = 10)
           
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
          
            ### for matplotlib
            self.fig = plt.figure(figsize = (5,3))
            self.canvas = FigureCanvasTkAgg(self.fig, master=root)
            self.toolbar = NavigationToolbar2TkAgg( self.canvas, root )
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)#grid(row = 0, column = 2)#
           
            self.ax = plt.subplot(111)
            self.ax.set_ylabel('signal [V]')
            self.ax.set_xlabel('t [s]')             
            self.ax.plot([1,4,2])
            self.ax2 = self.ax.twinx()
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
                    self.logger.debug( 'not attemp %d' % attemps_connect_to_chiller)
                    if attemps_connect_to_chiller == 3:

                        raise BaseException(
                                "Could not connect to chiller")

            self.read = int32()
            self.taskHandle = TaskHandle(0)
            self.nr_samples = 10
            self.data = init_channel(self.taskHandle,self.nr_samples,10000.0)
            self.logger.info('devices initialised')
            self.devices_initialised.set(1)

       
        def deleteData(self):
                self.t = []
                for i in range(self.k):
                        self.dat[i] = []
       
        def read_data_NI_daqmx(self):
            """ Read out the average voltage on channel one, and append it
            to self.dat"""
            data = read_voltage(self.taskHandle, self.nr_samples, self.data, self.read)
            for i in range(self.k):
              print "stdev: ", numpy.std(data)
              if numpy.std(data) > self.max_std_voltage_in_lock:
                  self.logger.error( "Probably out of lock. Suspending feedback")
                  self.outoflock=True
                  self.fig.set_facecolor('red')
              else :
                  self.outoflock = False
                  self.fig.set_facecolor('white')
              self.dat[i].append(numpy.average(self.data))
       
        def feedback_T(self):
            """ Feedback loop for the temperature 
            Check that the offset voltage is between the limits that were
            set. If not, change the temperature by .1 degree.
            
            """
            offset_voltage = self.offset_voltage
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
                    if abs(last_piezo_voltage -offset_voltage) < 0.05:
                            self.logger.debug(
                            'last piezo voltage was smaller \
                            0.05 V, device probably not locked')
                    else:
                        change_temperature = 0
                        # It is possible that we want to change the temperature
                        if last_piezo_voltage > self.Vpi_lim_high.get():
                            # voltage too high. Decrease the temperature
                            # by .1 degrees
                            # check when the last temperature change was
                            new_set_temp = self.T_set.get() - 1
                            #  check that the new set temperature is not
                            #  outside the limits
                            if new_set_temp > self.T_min.get():
                                self.T_set.set(new_set_temp)
                                change_temperature = 1
                            else:
                                self.logger.error('Temp feedback reached\
                                        higher specified limit')
                        if last_piezo_voltage < self.Vpi_lim_low.get():
                                new_set_temp = self.T_set.get() + 1
                                if new_set_temp < self.T_max.get():
                                    self.T_set.set(new_set_temp)
                                    change_temperature = 1
                                else:
                                    self.logger.error('Temp feedback\
                                            reached lower specified limit')

                        if change_temperature == 1:
                            self.logger.info(
                            'Changing baseplate temperature to %f degrees c'
                            % (self.T_set.get()/10.) )

                            # time.sleep(0.3)
                            try:
                                changedTemperature = serialChiller.setTemperature(serialPort = self.ser, temp = self.T_set.get())
                                self.logger.info(
                                        'CHANGED baseplate temperature at t = %d s to %d' % 
                                        (round(self.t[-1]), new_set_temp))
                            except:
                                self.logger.error('Could not change set \
temperature at t = %d' % self.t[-1])

                            if changedTemperature != -1 and changedTemperature > self.T_min.get() and changedTemperature < self.T_max.get():
                                #  double check it's okay
                                self.T_set.set(changedTemperature)
                            else: # in case just the reply from the changed temperature hanged, we ask for the temperature one more time manually
                                ##                                                        try:
##                                                                changedTemperature = readSetTemperature(self.ser)
##                                                        except:
##                                                                print 'WARNING - could not manually READ the set temperature at t = ',self.t[-1]
                                if changedTemperature != -1 and changedTemperature > self.T_min.get() and changedTemperature < self.T_max.get() :
                                    self.T_set.set(changedTemperature)
                                    print 'determined changed baseplate by manually asking, instead of the reply from serial_Chiller255p.setTemperature'

        def read_temperature_data(self):
            """ Reads the temperature data and appends it to
            self.temperature_data"""

            current_temp = serialChiller.readCoolantTemperature(serialPort = self.ser)
            self.temperature_data.append(current_temp)
            

        def mainLoop(self):
            """Main loop of the program. Checks wether we have to run
            anything, and starts running """

            # initialize the devices if the're not initialized yet
            if not self.devices_initialised.get():
                self.initSerialToChiller_and_NI_daqmx()
                self.logger.info('devices set up')
            
# stoploop is used to see if we have to continue running.
            self.stopLoop.set(0)

            if len(self.t) > 1: # if there's more than one record
                self.t0 =  time.time() - self.t[-1] # calculate dt
            else:
                self.t0 = time.time()

            while self.stopLoop.get() != 1:
                """ Main loop of the program """
                self.read_data_NI_daqmx()
                self.read_temperature_data()
                self.update_plots()
                #  if T_feedback is set, start the feedbback loop
                if self.T_feedback.get():
                    if self.outoflock == False:
                        self.feedback_T()
                    else:
                        self.logger.error("Out of lock!")
                root.update()
                time.sleep(self.sleep_time_per_meas.get()/1000.)

        def update_plots(self):
            """ Update the plots in the application """
            self.t.append(time.time() - self.t0)
            self.ax.clear()
            self.ax2.clear()
            n_sets_to_plot = self.sets_to_plot.get()
            n_sets_to_plot = min(n_sets_to_plot, len(self.t))
            if n_sets_to_plot <1:
                    n_sets_to_plot = 1
            # plot the last n_sets_to_plot, unless there is not enough
            # available
            line1 = self.ax.plot(self.t[-n_sets_to_plot:],
                    np.array(self.dat[0][-n_sets_to_plot:]),
                    label = 'piezo voltage comb')
            #  draw limit indicators
            self.drawlimits()
            # if custom limits are set, use them
            if self.limit_plot_y_axis.get():
                plt.ylim( self.y1lim.get(), self.y2lim.get() )
            line2 = self.ax2.plot(self.t[-n_sets_to_plot:],
                    self.temperature_data[-n_sets_to_plot:],'k',
                    label='coolant temperature')

            #  append labels
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            self.ax.legend(lines,labels,loc='lower left')
            self.ax2.set_ylabel('coolant temperature')
            self.ax.set_ylabel('Piezo voltage')
            self.ax.set_xlabel('time [s]')
            self.ax2.set_ylim((self.tmin/10.,self.tmax/10.))


            self.fig.canvas.draw()


        def drawlimits(self):
            """ Draw indicators for the lower limit, higher limit and the
            offset voltage"""
            xlim1, xlim2 = plt.xlim()
            high_limit = self.Vpi_lim_high.get()
            low_limit  = self.Vpi_lim_low.get()
            offset = self.offset_voltage

            self.ax.plot([xlim1,xlim2],
                    [offset, offset],
                    'r-.',label='offset voltage')

            self.ax.plot([xlim1,xlim2],
                    [high_limit,high_limit],
                    'r--',label='voltage limits')

            self.ax.plot([xlim1,xlim2],
                    [low_limit,low_limit],
                    'r--')



        def save(self):
            " Save the temperatures to a file "
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
                    self.logger.error('could not close serial connection')
                try:
                    if self.taskHandle.value != 0:
                        nidaq.DAQmxStopTask(self.taskHandle)
                        nidaq.DAQmxClearTask(self.taskHandle)
                except:
                    self.logger.error('could not close connection to NI device')
                plt.close('all')
                self.master.quit()


if __name__ == '__main__':
  root = Tk()

  root.title("Chiller feedback for Piezo")
  app = Application(root)
  root.mainloop()

  root.destroy()
