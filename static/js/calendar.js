let currentDate = new Date();

function renderCalendar(events = []) {
    const monthYear = document.getElementById('month-year');
    const daysContainer = document.getElementById('days');
    daysContainer.innerHTML = '';
    const month = currentDate.getMonth();
    const year = currentDate.getFullYear();
    monthYear.textContent = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
    const firstDay = new Date(year, month, 1).getDay();
    const lastDate = new Date(year, month + 1, 0).getDate();
    for (let i = 0; i < firstDay; i++) {
        daysContainer.innerHTML += '<div></div>';
    }
    for (let day = 1; day <= lastDate; day++) {
        const dayDiv = document.createElement('div');
        dayDiv.classList.add('day');
        dayDiv.textContent = day;
        if (day === new Date().getDate() && month === new Date().getMonth() && year === new Date().getFullYear()) {
            dayDiv.classList.add('today');
        }
        let eventHtml = '';
        events.forEach(event => {
            let eventDate = new Date(event.event_date);
            if (eventDate.getDate() === day && eventDate.getMonth() === month && eventDate.getFullYear() === year) {
                eventHtml += `<div class='event'>${event.event_name} @ ${event.event_time}</div>`;
            }
        });
        dayDiv.innerHTML += eventHtml;
        daysContainer.appendChild(dayDiv);
    }
}
function prevMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1);
    fetchEvents();
}
function nextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1);
    fetchEvents();
}
function fetchEvents() {
    fetch(`/getevents`)
        .then(response => response.json())
        .then(events => {
            if (Array.isArray(events)) {
                renderCalendar(events);  // Update the calendar
                
                // Update event list dynamically
                const list = document.getElementById('eventList');
                list.innerHTML = '';  // Clear previous list

                events.forEach((event, index) => {
                    list.innerHTML += `
                        <li id="event-${event.id}">
                            ${index + 1}. ${event.event_name}: ${event.event_date} ${event.event_time} - ${event.location}
                        </li>
                    `;
                });
            } else {
                console.error('Expected an array of events, but received:', events);
            }
        })
        .catch(error => console.error('Error fetching events:', error));
}

fetchEvents();  // Load events on page load
