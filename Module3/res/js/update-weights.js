function getWeights() {
    let a =  Array.from(document.getElementById("weights").tBodies[0].rows);
    a.pop();
    return a.map((e)=> {return parseFloat(e.cells[1].firstElementChild.value)})
}

function updateTotalIndicator() {
    const table = document.getElementById("table-assets");
    const tHead = table.tHead;
    const tBody = table.tBodies[0];
    const indicatorSet = new Set(
        Array.from(document.getElementById("weights").tBodies[0].rows)
            .map(e => { return e.cells[0].textContent.trim(); })
    );
    const idxArray = Array.from(tHead.rows[0].cells)
        .map((e, idx) => { return [idx, e.innerHTML] })
        .filter((e) => { return indicatorSet.has(e[1]) })
        .map((e) => { return e[0] });
    weights = getWeights();
    for (let row of tBody.rows) {
        row.cells[row.cells.length - 1].innerHTML = parseFloat(weights.reduce((t, w, i) => {
                return t + w * parseFloat(row.cells[idxArray[i]].innerHTML)
            }, 0).toFixed(4));
    }
}

function updateMeanStdTotalIndicator() {
    const tBody = document.getElementById("table-assets").tBodies[0];
    const mean = Array.from(tBody.rows).reduce((t, row) => {
        return t + parseFloat(row.cells[row.cells.length - 1].innerHTML);
    }, 0.0) / tBody.rows.length;
    const variance = Array.from(tBody.rows).reduce((t, row) => {
        return t + Math.pow(parseFloat(row.cells[row.cells.length - 1].innerHTML) - mean, 2);
    }, 0.0) / (tBody.rows.length - 1);
    const tW = document.getElementById("weights");
    const tWidxMean = Array.from(tW.tHead.rows[0].cells).map((c) => {return c.innerHTML.trim()}).indexOf("Mean");
    const tWidxStd = Array.from(tW.tHead.rows[0].cells).map((c) => {return c.innerHTML.trim()}).indexOf("Std.");
    const tWLength = tW.tBodies[0].rows.length;
    tW.tBodies[0].rows[tWLength - 1].cells[tWidxMean].innerHTML = mean.toFixed(4);
    tW.tBodies[0].rows[tWLength - 1].cells[tWidxStd].innerHTML = Math.sqrt(variance).toFixed(4);
}

document.querySelectorAll("input.weightInput").forEach(e => {
    e.addEventListener("keydown", (event) => {
        if (event.keyCode == 13) {
            e.blur();
        }
    });
});

document.querySelectorAll(".weightInput").forEach((rowWeight, i) => {
    rowWeight.addEventListener("focusout", () => {
        let indicatorRows = Array.from(document.getElementById("weights").tBodies[0].rows)
        let totalIndicatorRows = indicatorRows.pop()
        let indicatorWeights = indicatorRows.map(row => {
            return parseFloat(row.children[1].firstElementChild.value);
        });

        let totalSum = indicatorWeights.reduce((total, num) => { return total + num;}, 0);
        let totalDifference = 0.0;
        let nextIndicatorIndex = (i + 1) % indicatorRows.length;

        do { // Fix all weights when they are greater than 0. If lower than 0 only one iteration is needed
            totalDifference = totalSum - 1.0;
            indicatorWeights[nextIndicatorIndex] -= totalDifference;
            if (indicatorWeights[nextIndicatorIndex] < 0.0) {
                indicatorWeights[nextIndicatorIndex] = 0.0;
            }
            totalSum = indicatorWeights.reduce((total, num) => { return total + num;}, 0)
            nextIndicatorIndex = (nextIndicatorIndex + 1) % indicatorRows.length
        }
        while (totalSum > 1.0);
        
        for (let i = 0; i < indicatorWeights.length; i++) {
            indicatorRows[i].children[1].firstElementChild.value = parseFloat(indicatorWeights[i].toFixed(4));
        }

        updateTotalIndicator();
        updateMeanStdTotalIndicator();
    });
});
