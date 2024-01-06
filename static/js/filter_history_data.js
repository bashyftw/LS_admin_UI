class DataFilter {
    constructor(inputId, autoScrollToggle) {
        this.inputId = inputId;
        this.historyData = [];
        this.autoScrollToggle = autoScrollToggle;
        this.textareaId = 'history-textarea'; // Assuming a consistent ID pattern

        this.init();
    }

    init() {
        document.getElementById(this.inputId).addEventListener('input', () => this.filterData());
    }

    filterData() {
        var filter = document.getElementById(this.inputId).value.toLowerCase();
        var filteredEntries = this.historyData.filter(entry => {
            var controllerName = entry.data.split(',')[1].trim().toLowerCase();
            return controllerName.includes(filter);
        });

        filteredEntries.sort((a, b) => a.timestamp - b.timestamp);

        var filteredStrings = filteredEntries.map(entry => entry.data);
        var textarea = document.getElementById(this.textareaId);
        textarea.value = filteredStrings.join('\n');

        if (this.autoScrollToggle.autoScroll) {
            textarea.scrollTop = textarea.scrollHeight;
        }
    }

    push(data) {
        this.historyData.push(data);
    }
}

function formatDate(date) {
    let day = String(date.getDate()).padStart(2, '0');
    let month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based in JavaScript
    let hours = String(date.getHours()).padStart(2, '0');
    let minutes = String(date.getMinutes()).padStart(2, '0');
    let seconds = String(date.getSeconds()).padStart(2, '0');

    return `${day}/${month} ${hours}:${minutes}:${seconds}`;
}

function formatDateMillis(date) {
    let hours = String(date.getHours()).padStart(2, '0');
    let minutes = String(date.getMinutes()).padStart(2, '0');
    let seconds = String(date.getSeconds()).padStart(2, '0');
    let milliseconds = String(date.getMilliseconds()).padStart(3, '0'); // Milliseconds are from 0 to 999

    return `${hours}:${minutes}:${seconds}.${milliseconds}`;
}
