async function initReposTable(element) {
    // Fetch data from the repository
    const data = await fetch("/api/repos");

    if (!data.ok) {
        // TODO: error
        return;
    }

    const repos = JSON.parse(await data.text()).repos;
    // const dataAsArrays = repos.map();

    // Put data into table
    const managementTable = element.querySelector(".management-table");
    console.log(dataAsArrays);
    for (const { name, owner, linkedAt, modifiedAt } of repos) {
        const row = document.createElement("tr");
        managementTable.appendChild(row);

        const repoCell = document.createElement("td");
        // const repoCellLink = document.createElement("a","href")
        repoCell.textContent = `${owner}/${name}`;


    }

}


