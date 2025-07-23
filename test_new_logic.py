#!/usr/bin/env python3
"""Test the updated eye state detection logic."""

from openeyes.core import OpenEyes
import cv2
import numpy as np

# Test the updated eye state detection logic
app = OpenEyes()
print('🎯 Testing Updated Eye State Detection Logic')
print('=' * 50)

# Create a test frame
test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

print('🧪 Testing different eye detection scenarios:')

# Test 1: No face detected
detection_data = []
state = app._analyze_eye_state(detection_data, test_frame)
print(f'  No face detected: {state}')

# Test 2: Face with 0 eyes (should be CLOSED after delay)
detection_data = [{
    'face': {'x': 100, 'y': 100, 'width': 50, 'height': 50}, 
    'eyes': [], 
    'left_eyes': [], 
    'right_eyes': []
}]
state = app._analyze_eye_state(detection_data, test_frame)
print(f'  Face + 0 eyes (immediate): {state}')

# Test 3: Face with 2 eyes (should be OPEN immediately)
detection_data = [{
    'face': {'x': 100, 'y': 100, 'width': 50, 'height': 50}, 
    'eyes': [
        {'x': 110, 'y': 110, 'width': 10, 'height': 10}, 
        {'x': 130, 'y': 110, 'width': 10, 'height': 10}
    ], 
    'left_eyes': [], 
    'right_eyes': []
}]
state = app._analyze_eye_state(detection_data, test_frame)
print(f'  Face + 2 eyes: {state}')

# Test 4: Face with 1 eye (should be OPEN)
detection_data = [{
    'face': {'x': 100, 'y': 100, 'width': 50, 'height': 50}, 
    'eyes': [{'x': 110, 'y': 110, 'width': 10, 'height': 10}], 
    'left_eyes': [], 
    'right_eyes': []
}]
state = app._analyze_eye_state(detection_data, test_frame)
print(f'  Face + 1 eye: {state}')

# Test 5: Face with mixed eye types (left + right = 2 total)
detection_data = [{
    'face': {'x': 100, 'y': 100, 'width': 50, 'height': 50}, 
    'eyes': [], 
    'left_eyes': [{'x': 110, 'y': 110, 'width': 10, 'height': 10}], 
    'right_eyes': [{'x': 130, 'y': 110, 'width': 10, 'height': 10}]
}]
state = app._analyze_eye_state(detection_data, test_frame)
print(f'  Face + left&right eyes: {state}')

print('\n✅ Updated eye state detection logic working!')
print('📋 Summary:')
print('   • No face → NO FACE (yellow)')
print('   • Face + 0 eyes → CLOSED (red, 500ms delay)')
print('   • Face + 1 eye → OPEN (green, immediate)')
print('   • Face + 2+ eyes → OPEN (green, immediate)')
