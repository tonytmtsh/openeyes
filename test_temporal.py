#!/usr/bin/env python3
"""Test the temporal filtering logic for eye state detection."""

from openeyes.core import OpenEyes
import numpy as np
import time

app = OpenEyes()
print('🎯 Testing Temporal Filtering Logic')
print('=' * 50)

test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

print('🧪 Simulating eye detection sequence:')

# Start with open eyes (2 eyes detected)
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
print(f'1. Start with 2 eyes: {state}')

# Simulate eyes closing (0 eyes detected) - should still show OPEN initially
detection_data = [{
    'face': {'x': 100, 'y': 100, 'width': 50, 'height': 50}, 
    'eyes': [], 
    'left_eyes': [], 
    'right_eyes': []
}]
state = app._analyze_eye_state(detection_data, test_frame)
print(f'2. Eyes close (0 eyes) - immediate: {state}')

# Simulate multiple closed detections
for i in range(3):
    state = app._analyze_eye_state(detection_data, test_frame)
    print(f'3.{i+1}. Still 0 eyes: {state}')

# Simulate time passing (would normally be 500ms+)
time.sleep(0.1)  # Short sleep for demo
app.eyes_closed_start_time = time.time() - 0.6  # Simulate 600ms ago
state = app._analyze_eye_state(detection_data, test_frame)
print(f'4. After 600ms delay: {state}')

# Eyes open again
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
print(f'5. Eyes open again (2 eyes): {state}')

print('\n✅ Temporal filtering test complete!')
print('📋 Expected behavior:')
print('   • OPEN → immediate response')
print('   • CLOSED → 500ms delay before showing CLOSED')
print('   • NO FACE → immediate response')
