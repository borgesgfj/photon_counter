# Photon Counter with Timetagger

## Project Overview
 This project aims to create one software to acquire signals from a streaming time-to-digital converter called [TimeTagger](https://www.swabianinstruments.com/time-tagger/),
 and display or save the received data.
 In our basic experimental configuration, the Timetagger receives electric pulses from multiple photodetectors or from one photodetector detector with multiple
 input/output channels. In this way, the multiple Timetagger channels should be assigned to one detector ( or detector channel), it is done by physically 
 connecting the Timetagger with the detectors. Once the Timetagger channels are receiving electrical pulses from the detectors one user can have access
 to the data that is received by Timetagger and converted to a digital signal (a buffer), it is easily done by connecting the Timetagger to a computer via USB connection.

 Besides Timetagger provides a GUI to visualize the data it is not very useful from the most common use cases, and helpfully it provides an API that allows us
 to create programs in different languages to acquire, process, and visualize the converted signal. Also, this API has good documentation which can be found
 [here](https://www.swabianinstruments.com/static/documentation/TimeTagger/index.html).
 Another remarkable characteristic of Timetagger which we will explore in our project is that it can be operated remotely, by one computer in the same network
 that the computer in where the device is physically connected.
 This way the computer where the Timetagger is connected is called _server_, while the computer that attempts to remote connect is called _client_, in order to do
 this connection Timetagger official documentation recommends using `Pyro5` library in case of a Phyton program. This library establishes an RPC connection and
 the server will return to the client a _Proxy_ object which makes some methods available to the _client_ and will intermediate the communication between 
 _server_ and _client_.

## Project MVP
 - the initial version of this software aims to remotely connect to a Timetagger and obtain some data that should be displayed in real time
   to users as a `matplotlib` graph.
