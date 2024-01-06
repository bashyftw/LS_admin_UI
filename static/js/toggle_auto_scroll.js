class AutoScrollToggle {
    constructor(toggleButtonId, statusTextId) {
        this.autoScroll = true;
        this.toggleButton = document.getElementById(toggleButtonId);
        this.statusText = document.getElementById(statusTextId);

        if (!this.toggleButton) {
            console.error(`ToggleButton with ID '${toggleButtonId}' not found.`);
        }

        if (!this.statusText) {
            console.error(`StatusText with ID '${statusTextId}' not found.`);
        }

        this.init();
    }

    init() {
        this.toggleButton.addEventListener('click', () => {
            this.autoScroll = !this.autoScroll;
            this.updateStatusText();
        });
    }

    updateStatusText() {
        if (this.autoScroll) {
            this.statusText.textContent = 'Auto-Scroll On';
        } else {
            this.statusText.textContent = 'Auto-Scroll Off';
        }
    }
}
