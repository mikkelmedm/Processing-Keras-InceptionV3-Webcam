import oscP5.*;
import netP5.*;
import processing.video.*;
String firstValue;
String secondValue;
String stopValue;
  
OscP5 oscP5;
OscP5 oscP52;
Capture cam;
NetAddress myRemoteLocation;

void setup() {
  size(640, 480);
  frameRate(25);
  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this,1234);
  oscP52 = new OscP5(this,1234);
  myRemoteLocation = new NetAddress("127.0.0.1", 5005);
  
  String[] cameras = Capture.list();
  
  cam = new Capture(this, cameras[0]);
  cam.start();           
}
  

void draw() {
  if (cam.available() == true) {
    cam.read();
  } 
  set(0, 0, cam);
  
  if(stopValue==null && firstValue==null){
    textAlign(CENTER);
    textSize(25);
    text("mousepress to start",width/2,height/2+140);
    text("keypress to pause",width/2,height/2+160);
  }
   if(firstValue != null){
      textAlign(CENTER);
      fill(255);
      stroke(255);
      textSize(40);
      text(firstValue, width/2, height/2+130);
      text(secondValue, width/2, height/2+170);
  }
   if(stopValue != null){
      firstValue=null;
      secondValue=null;
      textSize(20);
      textSize(15);
      text(stopValue, width/2, height/2+140);
      stopValue = null;
  }
}

void keyPressed() {
  OscMessage myMessage = new OscMessage("/miklokey");
  myMessage.add("keypress");
  oscP52.send(myMessage, myRemoteLocation);
  print("sender - keypress");
}

void mousePressed() {
  OscMessage myMessage = new OscMessage("/miklo");
  
  myMessage.add(5);

  oscP5.send(myMessage, myRemoteLocation); 
  print("sent message");
}

void oscEvent(OscMessage theOscMessage) {  
  if(theOscMessage.checkAddrPattern("/isadora/1")==true) {
    firstValue = theOscMessage.get(0).stringValue();
    println(" values:"+ firstValue);
    return;
  } 
  if(theOscMessage.checkAddrPattern("/isadora/2")==true) {
    secondValue = theOscMessage.get(0).stringValue();
    println(" values:"+ secondValue);
    return;
  }
  if(theOscMessage.checkAddrPattern("/stopped")==true) {
    stopValue = theOscMessage.get(0).stringValue();
    println(" values:"+ stopValue);
    return;
  }
  println("### received an osc message. with address pattern "+theOscMessage.addrPattern());
}
