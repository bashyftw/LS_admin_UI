class VisSetting {
    constructor(groupsData, autoScrollToggle, inputId) {
        this.items = new vis.DataSet([]);
        this.container = document.getElementById('visualization');
        this.groups = new vis.DataSet(groupsData);
        this.input = document.getElementById(inputId);
        this.autoScrollToggle = autoScrollToggle;

        this.options = {
            start: new Date(Date.now() - 1000 * 60 * 1.5),  // One hour ago
            end: new Date(Date.now() + 1000 * 60 * 1.5),  // One hour from now
            format: {
                minorLabels: {
                    millisecond: 'x',
                    second: 's',
                    minute: 'HH:mm:ss',
                    hour: 'HH:mm:ss',
                    weekday: 'HH:mm:ss',
                    day: 'HH:mm:ss',
                    month: 'HH:mm:ss',
                    year: 'HH:mm:ss'
                }
            },
            margin: {
                item: 5,  // Change this to reduce the space between items
                axis: 5
            }
        };

        this.input.addEventListener('input', () => {
            var filter = this.input.value.toLowerCase();
            this.groups.forEach((group) => {
                var match = group.content.toLowerCase().includes(filter);
                this.groups.update({id: group.id, visible: match});
            });
        });

        this.timeline = new vis.Timeline(this.container, this.items, this.groups, this.options);

        this.startAutoScroll();
    }

    startAutoScroll() {
        setInterval(() => {
            var currentTime = new Date();
            this.items.forEach((item) => {
                if (item.active && item.end < currentTime) {
                    item.end = currentTime;
                    console.log(item.id);
                    this.items.update(item);
                }
                // var progress = ((currentTime - item.start) / (item.end - item.start)) * 100;
                // progress = Math.min(Math.max(Math.round(progress), 0), 100);  // Limit progress to 100%
                // item.content = item.file_name + ' ' + progress + '%';
                // this.items.update(item);
            });

            if (this.autoScrollToggle && this.autoScrollToggle.autoScroll) {
                this.timeline.moveTo(currentTime, {animation: {duration: 200, easingFunction: 'linear'}});
            }
        }, 200);
    }

    input_update(data) {
        let input_min_size = 2000;
        if (data.status === 'FALLING_EDGE') {
            var startTime = new Date(data.time_stamp);
            var endTime = new Date(startTime.getTime() + input_min_size);
            // Add a new item with the start time as the timestamp and the end time as 5 seconds later
            var item = {
                id: data.id + '-' + data.input,  // Generate a unique ID for each item
                group: data.id,
                content: 'Input ' + (data.input).toString(),
                start: startTime,
                end: endTime,
                active: true,
                style: 'background-color: lightgreen; color: black;',
                title: 'Input ' + (data.input).toString(),
            };
            this.items.add(item);
        } else if (data.status === 'RISING_EDGE') {
            // Find the existing item
            var item = this.items.get(data.id + '-' + data.input);
            if (item) {
                // Update the end time
                item.id = data.id + '-' + data.input + Date.now()
                if ((data.time_stamp - item.start) > input_min_size) {
                    item.end = data.time_stamp;
                }
                item.title = 'Input ' + (data.input).toString() + '<br>Duration:' + (Number(data.time_stamp) - Number(item.start)) + 'ms';

                item.active = false;
                this.items.add(item);
            }
            this.items.remove(data.id + '-' + data.input);

        }
    }

    audio_update(data) {
        var speaker_output = String(data.speaker_output).replace(/99/g, "-");
        if (data.status === 'ADDED') {
            var duration = String((data.end_time - data.start_time)/1000) + " Secs"

            var startTime = new Date(data.start_time);
            var item = {
                id: data.file_name + '-' + startTime,  // Generate a unique ID for each item
                group: data.id,
                content: data.file_name,
                start: startTime,
                end: new Date(data.end_time),
                style: 'background-color: lightyellow; color: black;',

                title: data.file_name + '<br>Speakers:' + speaker_output + '<br>Duration:' + duration
            };
            this.items.add(item);
        } else if (data.status === 'REMOVED') {
            var startTime = new Date(data.start_time);
            var item = this.items.get(data.file_name + '-' + startTime);
            if (item) {
                if (data.time_stamp < data.end_time) {
                    var duration = String((data.time_stamp - data.start_time)/1000) + " Secs"
                    item.end = data.time_stamp;
                    item.title= data.file_name + '<br>Speakers:' + speaker_output + '<br>Duration:' + duration  + ' - Ended early'
                    this.items.update(item);
                }

            }

        }
    }

    led_update(data) {
        if (data.status === 'ADDED') {

            var startTime = new Date(data.start_time);
            var item = {
                id: data.file_name + '-' + startTime,  // Generate a unique ID for each item
                group: data.id,
                content: data.file_name,
                start: startTime,
                end: new Date(data.end_time),
                style: 'background-color: lightblue; color: black;',
                title: data.file_name + '<br>Universes:' + data.universes
            };
            this.items.add(item);
        }
    }


}
