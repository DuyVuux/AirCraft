// Global variables
let employeeTimeline;
let aircraftTimeline;
const taskColors = {};

// Function to get or assign a color to a task code (with alpha)
function getTaskColor(taskCode, alpha = 0.85) {
    if (!taskColors[taskCode]) {
        const palette = [
            [59, 130, 246],   // blue
            [16, 185, 129],   // green
            [245, 158, 11],   // amber
            [239, 68, 68],    // red
            [139, 92, 246],   // violet
            [6, 182, 212],    // cyan
            [249, 115, 22],   // orange
            [132, 204, 22],   // lime
            [217, 70, 239],   // fuchsia
            [14, 165, 233]    // sky
        ];
        let hash = 0;
        for (let i = 0; i < taskCode.length; i++) {
            hash = taskCode.charCodeAt(i) + ((hash << 5) - hash);
        }
        const index = Math.abs(hash) % palette.length;
        taskColors[taskCode] = palette[index];
    }
    const [r, g, b] = taskColors[taskCode];
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Parse ISO time to Date object
function parseTime(isoStr) {
    return new Date(isoStr);
}

// Get timestamp in seconds from ISO string
function getTimestampSeconds(isoStr) {
    return Math.round(parseTime(isoStr).getTime() / 1000);
}

// Calculate duration in seconds
function getDurationSeconds(startTime, endTime) {
    return Math.round((parseTime(endTime) - parseTime(startTime)) / 1000);
}

// Format duration for display
function formatDuration(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}

async function loadData(filename) {
    try {
        const response = await fetch(`/api/data/${filename}`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        renderTimelines(data);
    } catch (error) {
        console.error('Error loading data:', error);
        alert('Failed to load data. See console for details.');
    }
}

function renderTimelines(data) {
    const solutionArray = data.solution || [];
    const employeesInfo = data.employeesInfo || {};
    const aircraftsInfo = data.aircraftsInfo || {};

    const employeeGroups = new vis.DataSet();
    const employeeItems = new vis.DataSet();
    const aircraftGroups = new vis.DataSet();
    const aircraftItems = new vis.DataSet();
    const aircraftSet = new Set();
    const employeeSet = new Set();

    let itemId = 1;

    // Process employees from solution
    for (const empData of solutionArray) {
        const empId = empData.employeeId;
        if (!empId || employeeSet.has(empId)) continue;
        employeeSet.add(empId);

        const empInfo = employeesInfo[empId] || {};
        const empLevel = empInfo.level || empData.level || 1;
        const empRole = empInfo.role || 'MECHANIC';

        employeeGroups.add({
            id: empId,
            content: `<div class="d-flex align-items-center">
                <i class="fas fa-user-circle me-2 text-primary"></i>
                <div>
                    <strong>${empId}</strong><br>
                    <small class="text-muted">${empRole} | Level ${empLevel}</small>
                </div>
            </div>`
        });

        // Working time backgrounds
        if (empInfo.workingTimes) {
            for (const wt of empInfo.workingTimes) {
                employeeItems.add({
                    id: itemId++,
                    group: empId,
                    content: '',
                    start: wt.start,
                    end: wt.end,
                    type: 'background',
                    className: 'vis-background-working'
                });
            }
        }

        // Break times
        if (empInfo.fixedBreakTimes) {
            for (const brk of empInfo.fixedBreakTimes) {
                employeeItems.add({
                    id: itemId++,
                    group: empId,
                    content: '',
                    start: brk.start,
                    end: brk.end,
                    type: 'background',
                    className: 'vis-background-break'
                });
                employeeItems.add({
                    id: itemId++,
                    group: empId,
                    content: '<i class="fas fa-coffee"></i> Break',
                    start: brk.start,
                    end: brk.end,
                    className: 'vis-item-break',
                    title: `<div class="tooltip-content">
                        <strong>Break Time</strong><br>
                        Start: ${brk.start}<br>
                        End: ${brk.end}<br>
                        Duration: ${formatDuration(getDurationSeconds(brk.start, brk.end))}
                    </div>`
                });
            }
        }

        // Task assignments
        if (empData.assignment) {
            empData.assignment.forEach(assign => {
                const task = assign.task;
                const aircraftId = task.aircraftId;
                const taskCode = task.taskCode;
                const color = getTaskColor(taskCode, 0.8);
                const solidColor = getTaskColor(taskCode, 1);

                const acInfo = aircraftsInfo[aircraftId] || {};
                const taskInfo = (acInfo.tasks || {})[taskCode] || {};
                const taskMinLevel = taskInfo.minLevel || 1;

                const startSec = getTimestampSeconds(assign.startTime);
                const endSec = getTimestampSeconds(assign.endTime);
                const durationSec = endSec - startSec;

                // Enhanced tooltip with seconds
                const tooltipContent = `
                    <div class="tooltip-content">
                        <strong>${taskCode}</strong>
                        <hr style="margin: 5px 0; border-color: rgba(255,255,255,0.3);">
                        <table style="font-size: 12px;">
                            <tr><td style="padding-right: 10px; color: #aaa;">Employee:</td><td>${empId} (Lvl ${empLevel})</td></tr>
                            <tr><td style="padding-right: 10px; color: #aaa;">Aircraft:</td><td>${aircraftId}</td></tr>
                            <tr><td style="padding-right: 10px; color: #aaa;">Task Level:</td><td>${taskMinLevel}</td></tr>
                            <tr><td style="padding-right: 10px; color: #aaa;">Location:</td><td>${assign.locationId || 'N/A'}</td></tr>
                            <tr><td colspan="2" style="padding-top: 5px; border-top: 1px solid rgba(255,255,255,0.2);"></td></tr>
                            <tr><td style="padding-right: 10px; color: #aaa;">Start:</td><td>${assign.startTime}</td></tr>
                            <tr><td style="padding-right: 10px; color: #60a5fa;"><b>Start (s):</b></td><td><b>${startSec}</b></td></tr>
                            <tr><td style="padding-right: 10px; color: #aaa;">End:</td><td>${assign.endTime}</td></tr>
                            <tr><td style="padding-right: 10px; color: #60a5fa;"><b>End (s):</b></td><td><b>${endSec}</b></td></tr>
                            <tr><td style="padding-right: 10px; color: #aaa;">Duration:</td><td>${durationSec}s (${formatDuration(durationSec)})</td></tr>
                        </table>
                    </div>
                `;

                // Employee timeline item
                employeeItems.add({
                    id: itemId++,
                    group: empId,
                    content: `<div class="vis-item-content"><i class="fas fa-tools"></i> ${taskCode}</div>`,
                    start: assign.startTime,
                    end: assign.endTime,
                    style: `background-color: ${color}; border-color: ${solidColor}; color: white;`,
                    title: tooltipContent
                });

                // Aircraft group
                if (!aircraftSet.has(aircraftId)) {
                    aircraftSet.add(aircraftId);
                    aircraftGroups.add({
                        id: aircraftId,
                        content: `<div class="d-flex align-items-center">
                            <i class="fas fa-plane me-2 text-accent"></i>
                            <strong>${aircraftId}</strong>
                        </div>`
                    });
                    // Time window background
                    if (acInfo.timeWindow) {
                        aircraftItems.add({
                            id: itemId++,
                            group: aircraftId,
                            content: '',
                            start: acInfo.timeWindow.start,
                            end: acInfo.timeWindow.end,
                            type: 'background',
                            className: 'vis-background-working'
                        });
                    }
                }

                // Aircraft timeline item (with transparency)
                aircraftItems.add({
                    id: itemId++,
                    group: aircraftId,
                    content: `<div class="vis-item-content"><i class="fas fa-clipboard-check"></i> ${taskCode}</div>`,
                    start: assign.startTime,
                    end: assign.endTime,
                    style: `background-color: ${color}; border-color: ${solidColor}; color: white;`,
                    title: tooltipContent
                });
            });
        }
    }

    // Employee timeline options (no stacking - 1 employee = 1 task at a time)
    const empOptions = {
        stack: false,
        editable: false,
        margin: { item: 10, axis: 5 },
        orientation: 'top',
        zoomKey: 'ctrlKey',
        maxHeight: '600px',
        verticalScroll: true,
        tooltip: {
            followMouse: true,
            overflowMethod: 'cap'
        }
    };

    // Aircraft timeline options (stacking = true - multiple tasks can overlap)
    const acOptions = {
        stack: true,
        editable: false,
        margin: { item: 5, axis: 5 },
        orientation: 'top',
        zoomKey: 'ctrlKey',
        maxHeight: '600px',
        verticalScroll: true,
        tooltip: {
            followMouse: true,
            overflowMethod: 'cap'
        }
    };

    const empContainer = document.getElementById('employee-timeline');
    employeeTimeline = new vis.Timeline(empContainer, employeeItems, employeeGroups, empOptions);

    const airContainer = document.getElementById('aircraft-timeline');
    aircraftTimeline = new vis.Timeline(airContainer, aircraftItems, aircraftGroups, acOptions);
}
