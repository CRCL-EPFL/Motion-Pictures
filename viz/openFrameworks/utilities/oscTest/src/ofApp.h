#pragma once

#include "ofMain.h"
#include "ofxOsc.h"

// send host (aka ip address)
#define HOST "localhost"

/// send port
#define PORT 7777

// demonstrates sending OSC messages with an ofxOscSender,
// use in conjunction with the oscReceiveExample
class ofApp : public ofBaseApp{

	public:

		void setup();
		void update();
		void draw();

		void keyPressed(int key);
		void keyReleased(int key);
		void mouseMoved(int x, int y);
		void mouseDragged(int x, int y, int button);
		void mousePressed(int x, int y, int button);
		void mouseReleased(int x, int y, int button);
		void mouseEntered(int x, int y);
		void mouseExited(int x, int y);
		void windowResized(int w, int h);
		void dragEvent(ofDragInfo dragInfo);
		void gotMessage(ofMessage msg);

		ofTrueTypeFont font;
		ofxOscSender sender;
		ofBuffer imgAsBuffer;
		ofImage img;
    
        int keyVal;
    
    bool active;
    float disCount;
    
    // Maximum disappeared
    float maxDis;
    bool disappeared;
};
