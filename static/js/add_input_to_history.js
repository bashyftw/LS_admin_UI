function addInputToHistory(data, historyDict) {
    var controller = data.name + ",";
    var time_stamp = formatDate(new Date(data.time_stamp)) + ","
    var status = data.status + ",";
    var input_id = data.input + ",";
    var str_data =
        time_stamp.padEnd(17) +
        controller.padEnd(25) +
        " input: " +
        input_id.padEnd(10) +
        " COV: " +
        status.padEnd(35)

    ;
    historyDict.push({timestamp: data.time_stamp, data: str_data});
    historyDict.filterData();
}