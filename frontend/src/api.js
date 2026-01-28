/**
 * API Service for Synapses Room Scheduler
 */

const API_BASE = '/api';

export async function fetchRooms() {
    try {
        const res = await fetch(`${API_BASE}/rooms`);
        const data = await res.json();
        return data;
    } catch (error) {
        console.error("Error fetching rooms:", error);
        return { success: false, error: error.message };
    }
}

export async function fetchAllSchedules() {
    try {
        // Get today's date
        const today = new Date().toISOString().split('T')[0];
        const res = await fetch(`${API_BASE}/schedules?start=${today}&end=${today}`);
        const data = await res.json();
        return data;
    } catch (error) {
        console.error("Error fetching schedules:", error);
        return { success: false, error: error.message };
    }
}

export async function login(username, password) {
    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        return await res.json();
    } catch (error) {
        return { success: false, error: error.message };
    }
}

export async function checkAuth() {
    try {
        const res = await fetch(`${API_BASE}/auth/status`);
        const data = await res.json();
        return data;
    } catch (error) {
        return { authenticated: false };
    }
}

export async function fetchRoomSchedule(roomId) {
    try {
        const today = new Date();
        const nextWeek = new Date();
        nextWeek.setDate(today.getDate() + 7);

        const startStr = today.toISOString().split('T')[0];
        const endStr = nextWeek.toISOString().split('T')[0];

        // Fetch 7 days schedule
        const res = await fetch(`${API_BASE}/schedule/${roomId}?start=${startStr}&end=${endStr}`);
        const data = await res.json();
        return data; // returns { success: true, events: [...] }
    } catch (error) {
        console.error("Error fetching room schedule:", error);
        return { success: false, error: error.message };
    }
}

export async function getUser() {
    try {
        const res = await fetch(`${API_BASE}/user`);
        const data = await res.json();
        return data; // { success: true, user: { name: "..." } }
    } catch (error) {
        return { success: false };
    }
}
