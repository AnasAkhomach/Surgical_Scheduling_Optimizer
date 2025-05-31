# Surgery Scheduling System - Manual Test Checklist

## Test Execution Information
**QA Engineer**: Senior QA Engineer AI  
**Test Date**: [TO BE FILLED]  
**Environment**: Development  
**Browser**: Chrome/Firefox/Safari  
**Frontend URL**: http://localhost:3000  
**Backend URL**: http://localhost:8000  

## Pre-Test Setup Checklist
- [ ] Backend server is running (`python -m uvicorn api.main:app --reload`)
- [ ] Frontend server is running (`npm run dev`)
- [ ] Database is populated with test data
- [ ] Test user account exists (username: testuser, password: testpass123)
- [ ] Browser developer tools are open for monitoring

---

## Test Suite 1: Authentication & Navigation

### TC001: User Login
**Priority**: Critical  
**Estimated Time**: 3 minutes

**Pre-conditions**: User is not logged in

**Test Steps**:
1. Navigate to application URL
2. Verify login form is displayed
3. Enter valid credentials (testuser/testpass123)
4. Click "Login" button
5. Verify successful login and dashboard access

**Expected Results**:
- [ ] Login form displays correctly
- [ ] Valid credentials are accepted
- [ ] User is redirected to dashboard
- [ ] Navigation menu is visible
- [ ] User profile/logout option is available

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

### TC002: Navigation Between Screens
**Priority**: High  
**Estimated Time**: 5 minutes

**Test Steps**:
1. From dashboard, navigate to Surgery Scheduling
2. Navigate to Resource Management
3. Navigate to SDST Management
4. Navigate to Reports/Analytics
5. Return to Dashboard

**Expected Results**:
- [ ] All navigation links work correctly
- [ ] Page transitions are smooth
- [ ] No console errors during navigation
- [ ] Active page is highlighted in navigation

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

---

## Test Suite 2: Surgery Scheduling Core Functionality

### TC003: Schedule Data Loading
**Priority**: Critical  
**Estimated Time**: 5 minutes

**Test Steps**:
1. Navigate to Surgery Scheduling screen
2. Verify schedule loads within 5 seconds
3. Check if surgeries are displayed in Gantt chart
4. Verify surgery details are complete
5. Test date navigation (previous/next day)

**Expected Results**:
- [ ] Schedule loads within 5 seconds
- [ ] Gantt chart displays correctly
- [ ] Surgery items show: patient name, type, surgeon, time
- [ ] Date navigation works correctly
- [ ] Loading indicators appear during data fetch

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

### TC004: Run Optimization Workflow
**Priority**: Critical  
**Estimated Time**: 10 minutes

**Test Steps**:
1. On Surgery Scheduling screen, locate "Run Optimization" button
2. Click the optimization button
3. Verify optimization starts (loading indicator)
4. Wait for optimization to complete (max 30 seconds)
5. Verify optimization results are displayed
6. Check if suggestions are actionable

**Expected Results**:
- [ ] Optimization button is clearly visible
- [ ] Loading indicator appears when optimization starts
- [ ] Optimization completes within 30 seconds
- [ ] Results show score and improvements
- [ ] Suggestions are clearly presented
- [ ] "Apply Results" option is available

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

### TC005: Apply Optimization Results
**Priority**: High  
**Estimated Time**: 5 minutes

**Pre-conditions**: Optimization has been run successfully

**Test Steps**:
1. Review optimization suggestions
2. Click "Apply Results" or similar button
3. Verify schedule updates with new assignments
4. Check if changes persist after page refresh
5. Verify no data corruption occurred

**Expected Results**:
- [ ] Apply button works correctly
- [ ] Schedule updates immediately
- [ ] Changes are saved to backend
- [ ] No data loss or corruption
- [ ] Success message is displayed

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

---

## Test Suite 3: Resource Management

### TC006: Operating Rooms Management
**Priority**: High  
**Estimated Time**: 8 minutes

**Test Steps**:
1. Navigate to Resource Management screen
2. Click on Operating Rooms tab
3. Verify list of operating rooms loads
4. Test adding a new operating room
5. Test editing an existing operating room
6. Test deleting an operating room (if safe)

**Expected Results**:
- [ ] OR list loads correctly
- [ ] Add new OR form works
- [ ] Edit OR functionality works
- [ ] Delete OR works (with confirmation)
- [ ] Changes persist after page refresh
- [ ] Proper validation messages appear

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

### TC007: Staff Management
**Priority**: High  
**Estimated Time**: 8 minutes

**Test Steps**:
1. Navigate to Staff tab in Resource Management
2. Verify staff list loads with roles and specializations
3. Test adding a new staff member
4. Test editing staff member details
5. Verify staff appears in surgery assignment options

**Expected Results**:
- [ ] Staff list displays correctly
- [ ] Add staff form works properly
- [ ] Edit staff functionality works
- [ ] Staff roles are properly categorized
- [ ] New staff appears in scheduling options

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

---

## Test Suite 4: SDST Management

### TC008: SDST Matrix Viewing
**Priority**: Medium  
**Estimated Time**: 5 minutes

**Test Steps**:
1. Navigate to SDST Management screen
2. Verify SDST matrix loads
3. Check if surgery types are listed
4. Verify setup times are displayed correctly
5. Test matrix navigation and readability

**Expected Results**:
- [ ] SDST matrix loads without errors
- [ ] Surgery types are clearly listed
- [ ] Setup times are displayed in minutes
- [ ] Matrix is readable and well-formatted
- [ ] No missing or corrupted data

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

### TC009: SDST Matrix Editing
**Priority**: Medium  
**Estimated Time**: 8 minutes

**Test Steps**:
1. Select a cell in the SDST matrix
2. Edit the setup time value
3. Save the changes
4. Verify changes persist after page refresh
5. Test impact on optimization calculations

**Expected Results**:
- [ ] Matrix cells are editable
- [ ] Input validation works correctly
- [ ] Changes save successfully
- [ ] Data persists after refresh
- [ ] Changes affect optimization results

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

---

## Test Suite 5: Error Handling & Edge Cases

### TC010: Network Error Handling
**Priority**: High  
**Estimated Time**: 10 minutes

**Test Steps**:
1. With application running, stop the backend server
2. Try to perform various operations (load schedule, run optimization)
3. Verify error messages are user-friendly
4. Restart backend server
5. Verify application recovers gracefully

**Expected Results**:
- [ ] Clear error messages appear
- [ ] Application doesn't crash
- [ ] No confusing technical errors shown to user
- [ ] Application recovers when backend returns
- [ ] Data integrity is maintained

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

### TC011: Large Dataset Handling
**Priority**: Medium  
**Estimated Time**: 5 minutes

**Test Steps**:
1. Load a schedule with many surgeries (20+)
2. Verify performance remains acceptable
3. Test optimization with large dataset
4. Check memory usage in browser dev tools
5. Verify UI remains responsive

**Expected Results**:
- [ ] Large datasets load within 10 seconds
- [ ] UI remains responsive
- [ ] No memory leaks detected
- [ ] Optimization still completes within time limit
- [ ] Gantt chart renders correctly

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

---

## Test Suite 6: User Experience & Usability

### TC012: Interface Responsiveness
**Priority**: Medium  
**Estimated Time**: 5 minutes

**Test Steps**:
1. Test application on different screen sizes
2. Verify mobile responsiveness (if applicable)
3. Check if all buttons and links are easily clickable
4. Verify text is readable at all sizes
5. Test keyboard navigation

**Expected Results**:
- [ ] Interface adapts to different screen sizes
- [ ] All interactive elements are accessible
- [ ] Text remains readable
- [ ] Keyboard navigation works
- [ ] No UI elements overlap or become unusable

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

### TC013: Data Validation & Feedback
**Priority**: High  
**Estimated Time**: 8 minutes

**Test Steps**:
1. Try to submit forms with invalid data
2. Test required field validation
3. Verify success messages appear for successful operations
4. Check if loading states are clearly indicated
5. Test confirmation dialogs for destructive actions

**Expected Results**:
- [ ] Invalid data is rejected with clear messages
- [ ] Required fields are properly validated
- [ ] Success messages confirm completed actions
- [ ] Loading states are clearly visible
- [ ] Destructive actions require confirmation

**Actual Results**: _______________  
**Status**: ⬜ Pass ⬜ Fail ⬜ Blocked  
**Notes**: _______________

---

## Test Execution Summary

### Overall Test Results
**Total Test Cases**: 13  
**Passed**: _____ / 13  
**Failed**: _____ / 13  
**Blocked**: _____ / 13  
**Success Rate**: _____%

### Critical Issues Found
1. _______________
2. _______________
3. _______________

### High Priority Issues Found
1. _______________
2. _______________
3. _______________

### Recommendations
1. _______________
2. _______________
3. _______________

### Sign-off
**QA Engineer**: _______________  
**Date**: _______________  
**Overall Status**: ⬜ PASS ⬜ FAIL ⬜ CONDITIONAL PASS  

### Notes for Development Team
_______________
_______________
_______________

---

## Appendix: Browser Console Log Analysis

### JavaScript Errors Found
- [ ] No critical JavaScript errors
- [ ] Minor warnings only
- [ ] Critical errors found (list below):

### Network Request Analysis
- [ ] All API calls complete successfully
- [ ] Response times are acceptable (<200ms for CRUD, <30s for optimization)
- [ ] No failed requests
- [ ] Issues found (list below):

### Performance Observations
- [ ] Page load times are acceptable
- [ ] Memory usage is reasonable
- [ ] No performance bottlenecks identified
- [ ] Performance issues found (list below):
