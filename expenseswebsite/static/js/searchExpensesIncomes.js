const searchField = document.querySelector('#searchField');
const tableOutput = document.querySelector('.table-output');
const appTable = document.querySelector('.app-table');
const p_not_found = document.querySelector('.not_found')
const tbody = document.querySelector('.table-body');
tableOutput.style.display = "none";
p_not_found.style.display = "none";
let url = "";
if (document.location.pathname === '/'){
     url = "http://127.0.0.1:8000"+document.location.pathname+"search_expenses/";
} else {
    url = "http://127.0.0.1:8000"+document.location.pathname+"search_incomes/";
}



searchField.addEventListener('keyup', (e) => {

    const searchValue = e.target.value;

    if (searchValue.trim().length > 0) {
        tbody.innerHTML="";


        fetch(url, {
            body: JSON.stringify({searchText: searchValue}),
            method: "POST",
        }).then((res) => res.json())
            .then((data) => {
                tableOutput.style.display = "block";
                appTable.style.display = "none";

                if (data.length === 0) {
                    p_not_found.style.display = "block";
                } else {
                    data.forEach(item => {
                        tbody.innerHTML += `
                    <tr>
                    <td> ${item.amount} </td>
                    <td>${item.category || item.source}</td>
                    <td>${item.description}  </td>
                    <td> ${item.date} </td>
                    </tr>
                    `

                    })

                }
            });


    } else {
        appTable.style.display = "block";
        tableOutput.style.display = "none";
        p_not_found.style.display = "none"
    }

})