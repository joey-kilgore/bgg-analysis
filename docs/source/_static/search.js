// search.js
function searchTable(searchBarId, tableId) {
    const input = document.getElementById(searchBarId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const trs = table.getElementsByTagName("tr");

    for (let i = 1; i < trs.length; i++) {
        const tds = trs[i].getElementsByTagName("td");
        const imgAlt = tds[0].getElementsByTagName("img")[0].alt.toLowerCase();
        let match = imgAlt.indexOf(filter) > -1;

        // Loop through the remaining columns to check for usernames
        for (let j = 1; j < tds.length; j++) {
            const owners = tds[j].textContent.toLowerCase();
            if (owners.indexOf(filter) > -1) {
                match = true;
                break;
            }
        }

        // Show or hide the row based on the match
        trs[i].style.display = match ? "" : "none";
    }
}
