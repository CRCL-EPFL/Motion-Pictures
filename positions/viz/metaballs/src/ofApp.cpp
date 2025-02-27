#include "ofApp.h"

//--------------------------------------------------------------
void ofApp::setup() {
	ofBackground(255);
	ofSetCircleResolution(200);

	int width = 1920;
	int height = 1200;

    ofHideCursor();

	shader.load("shaders/shader");

	// GUI
	/*parameters.setName("Calibration");
	parameters.add(gamma.set("Gamma", 2.0, 1.0, 3.0));
	parameters.add(blendExp.set("Blend Power", 2, 1, 3));
	parameters.add(overlap.set("Overlap", 120, 0, 240));
	gui.setup(parameters);*/

    ofLog() << "Listening for OSC messages on port " << PORT;
    receiver.setup(PORT);
}

//--------------------------------------------------------------
void ofApp::update() {
    while (receiver.hasWaitingMessages()) {
        ofxOscMessage m;
        receiver.getNextMessage(m);

        // pre-process message into vector
        if (m.getAddress() == "/points") {
            // length is the number of complete objects, total message length / number of parameters
            // Parameters include (in order): id, x pos, y pos, dest x, dest y
            int length = m.getNumArgs() / base;

            for (int i = 0; i < length; i++) {
                int baseInd = i * base;

                // get ID
                int id = m.getArgAsInt(baseInd);
                // get coordinates
                // might not need to scale to resolution as shader will undo
                int tempX = int(m.getArgAsFloat(baseInd + 1) * ofGetWidth());
                int tempY = int(m.getArgAsFloat(baseInd + 2) * ofGetHeight());

                cout << "x: " << tempX << ", y: " << tempY << endl;

                                // for later use, move message info into messageStores
                if (ballMap.find(id) != ballMap.end()) {
                    //                    cout << "Found " << id << " x: " << tempX << endl;
                    ballMap[id].update(tempX, tempY);
                }
            }
        }

        else if (m.getAddress() == "/points/create") {
            int id = m.getArgAsInt(0);

            int tempX = int(m.getArgAsFloat(1) * ofGetWidth());
            int tempY = int(m.getArgAsFloat(2) * ofGetHeight());

            Ball tempBall;
            ballMap.insert(make_pair(id, tempBall));

            ballMap[id].setup(id);
        }

        else if (m.getAddress() == "/points/delete") {
            int id = m.getArgAsInt(0);

            ballMap[id].setDeleteAnimation();
        }
    }

    if (ballMap.size() > 0) {
        // flatten everything to be passed as uniform
        int it = 0;
        int singleIt = 0;
        for (auto& comp : ballMap) {
            flatCoords[it] = comp.second.x;
            flatCoords[it + 1] = comp.second.y;

            flatHues[it] = comp.second.hue;


            flatMoveFrames[it] = comp.second.moveFrame;
            flatDisFrames[it] = comp.second.disFrame;

            it += 2;
        }
    }

    if (disappearStore.size() > 0) {
        //        cout << "disappearStore size > 0" << endl;
                // not ideal, since for deletion will search through entire disappearStore(), look into threading and mutex
        for (int i = 0; i < disappearStore.size(); i++) {
            ballMap[disappearStore[i]].disappear();
            //            cout << "disappearStore id " << disappearStore[i] << endl;
        }
    }
}

//--------------------------------------------------------------
void ofApp::draw() {

    float flatTest[20]{};
    /*flatTest[0] = mouseX;
    flatTest[1] = mouseY;*/
    
    //std:cout << flatTest[0] << " " << flatTest[1] << endl;

    shader.begin();

    shader.setUniform1f("u_time", ofGetElapsedTimef());
    shader.setUniform2f("u_res", ofGetWidth(), ofGetHeight());
    shader.setUniform2f("u_mouse", mouseX, mouseY);
    shader.setUniform1i("num", ballMap.size());
    shader.setUniform1fv("pos", &flatCoords[0], ballMap.size() * 2);
    //shader.setUniform1i("num", 1);
    //// Pass in address of array start
    //shader.setUniform1fv("pos", &flatTest[0], 2);
    ofColor(0);
    ofDrawRectangle(0, 0, ofGetWidth(), ofGetHeight());    
    
    shader.end();
	
	// instructions
	ofSetColor(225);

	//gui.draw();
}

// callback on delete event
void ofApp::delBall(int& key) {
    cout << "In delHalo" << endl;
    //    disappearStore.erase(key);
        // iterate through vector and delete corresponding value holding key
    vector<int>::iterator it = disappearStore.begin();
    for (; it != disappearStore.end(); ) {
        if (*it == key) {
            it = disappearStore.erase(it);
        }
        else {
            ++it;
        }
    }

    cout << "Store size: " << disappearStore.size() << endl;
    ballMap.erase(key);
    cout << "Past erase" << endl;
}


//--------------------------------------------------------------
void ofApp::keyPressed(int key) {
}

//--------------------------------------------------------------
void ofApp::keyReleased(int key) {

}

//--------------------------------------------------------------
void ofApp::mouseMoved(int x, int y) {

}

//--------------------------------------------------------------
void ofApp::mouseDragged(int x, int y, int button) {

}

//--------------------------------------------------------------
void ofApp::mousePressed(int x, int y, int button) {

}

//--------------------------------------------------------------
void ofApp::mouseReleased(int x, int y, int button) {

}

//--------------------------------------------------------------
void ofApp::mouseEntered(int x, int y) {

}

//--------------------------------------------------------------
void ofApp::mouseExited(int x, int y) {

}

//--------------------------------------------------------------
void ofApp::windowResized(int w, int h) {

}

//--------------------------------------------------------------
void ofApp::gotMessage(ofMessage msg) {

}

//--------------------------------------------------------------
void ofApp::dragEvent(ofDragInfo dragInfo) {

}
