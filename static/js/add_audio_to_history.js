function addAudioToHistory(data, historyDict) {
    var controller = data.name + ",";
    var starttime = "S: " + formatDateMillis(new Date(data.start_time))
    var endtime = "E: " + formatDateMillis(new Date(data.end_time))
    var time_stamp = formatDate(new Date(data.time_stamp)) + ","
    var duration = "  D: " + ((Number(data.end_time) - Number(data.start_time)) / 1000).toFixed(2);
    var speaker_output = String(data.speaker_output).replace(/99/g, "-");
    var speakers = " Speakers: " + speaker_output;
    var status = data.status + ",";
    var filename = data.file_name + ",";
    var addr = data.ip + ",";
    console.log(controller.padEnd(20).length)
    var str_data =
        time_stamp.padEnd(17) +
        controller.padEnd(25) +
        " Audio:   " +
        status.padEnd(16) +
        filename.padEnd(30) +
        starttime +
        endtime +
        duration +
        speakers
    ;
    historyDict.push({timestamp: data.time_stamp, data: str_data});
    historyDict.filterData();
}

