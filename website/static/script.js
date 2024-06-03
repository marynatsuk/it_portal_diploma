//This file contains js scripts that are applicable for all three users
// SIDE TOGGLE
const body = document.querySelector("body"),
  modeToggle = body.querySelector(".mode-toggle");
sidebar = body.querySelector("nav");
sidebarToggle = body.querySelector(".sidebar-toggle");

let getStatus = localStorage.getItem("status");
if (getStatus && getStatus === "close") {
  sidebar.classList.toggle("close");
}

sidebarToggle.addEventListener("click", () => {
  sidebar.classList.toggle("close");
  if (sidebar.classList.contains("close")) {
    localStorage.setItem("status", "close");
  } else {
    localStorage.setItem("status", "open");
  }
});

//SEARCH FUNCTION
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.querySelector(".search-box input");
  const tables = [
    document.querySelectorAll("#adminUserTable tr"),
    document.querySelectorAll("#managerTableBody tr"),
    document.querySelectorAll("#managerDeviceTableBody tr"),
    document.querySelectorAll("#managerWorkerTableBody tr"),
    document.querySelectorAll("#managerRequestTableBody tr"),
    document.querySelectorAll("#userTableBody tr"),
    document.querySelectorAll("#userRequestsTableBody tr"),
    document.querySelectorAll("#userDeviceTableBody tr"),
  ];

  function performSearch() {
    const searchQuery = searchInput.value.toLowerCase();
    tables.forEach((tableRows) => {
      tableRows.forEach((row) => {
        const rowText = row.textContent.toLowerCase();
        row.style.display = rowText.includes(searchQuery) ? "" : "none";
      });
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", performSearch);
  }
});

//SORT TABLES ON CLICK TO HEADER
document.addEventListener("DOMContentLoaded", function () {
  const table = document.querySelector(".activity-data table");

function sortTable(columnIndex, order) {
    if (table) {
      const tableRows = Array.from(table.querySelectorAll("tbody tr"));
      tableRows.sort((rowA, rowB) => {
        const cellA = rowA.cells[columnIndex].textContent.trim();
        const cellB = rowB.cells[columnIndex].textContent.trim();

        if (columnIndex === 0) {
          return parseInt(cellA) - parseInt(cellB);
        }

        if (order === "asc") {
          return cellA.localeCompare(cellB);
        } else {
          return cellB.localeCompare(cellA);
        }
      });

      tableRows.forEach((row) => {
        table.querySelector("tbody").appendChild(row);
      });
      const headers = table.querySelectorAll("thead th");
      headers.forEach((header, index) => {
        header.addEventListener("click", () => {
          const isAscending = header.classList.contains("asc");
          headers.forEach((header) => header.classList.remove("asc", "desc"));
          if (isAscending) {
            header.classList.add("desc");
            sortTable(index, "desc");
          } else {
            header.classList.add("asc");
            sortTable(index, "asc");
          }
        });
      });
    }
  }
});

//PAGES NAVIGATION
document.addEventListener("DOMContentLoaded", function () {
  const entriesSelect = document.getElementById("entriesSelect");
  const tableBodies = [
    document.getElementById("adminUserTable"),
    document.getElementById("managerTableBody"),
    document.getElementById("managerDeviceTableBody"),
    document.getElementById("managerWorkerTableBody"),
    document.getElementById("managerRequestTableBody"),
    document.getElementById("userTableBody"),
    document.getElementById("userRequestsTableBody"),
    document.getElementById("userDeviceTableBody"),
  ].filter((tableBody) => tableBody !== null);

  const firstPageButton = document.getElementById("firstPage");
  const prevPageButton = document.getElementById("prevPage");
  const nextPageButton = document.getElementById("nextPage");
  const lastPageButton = document.getElementById("lastPage");
  const pageNumberSpan = document.getElementById("pageNumber");

  let currentPage = 1;
  let entriesPerPage = entriesSelect
    ? entriesSelect.value === "all"
      ? Infinity
      : parseInt(entriesSelect.value)
    : 10;

  function updateTable() {
    tableBodies.forEach((tableBody) => {
      const rows = Array.from(tableBody.getElementsByTagName("tr"));
      let start = 0;
      let end = rows.length;

      if (entriesPerPage !== Infinity) {
        start = (currentPage - 1) * entriesPerPage;
        end =
          entriesPerPage === Infinity ? rows.length : start + entriesPerPage;
      }

      rows.forEach((row, index) => {
        row.style.display = index >= start && index < end ? "" : "none";
      });

      updatePaginationButtons(rows.length);
    });

    if (pageNumberSpan) {
      pageNumberSpan.textContent = currentPage;
    }
  }

  function updatePaginationButtons(totalRows) {
    const totalPages =
      entriesPerPage === Infinity ? 1 : Math.ceil(totalRows / entriesPerPage);

    firstPageButton.disabled = currentPage === 1 || totalPages === 1;
    prevPageButton.disabled = currentPage === 1 || totalPages === 1;
    nextPageButton.disabled = currentPage === totalPages || totalPages === 1;
    lastPageButton.disabled = currentPage === totalPages || totalPages === 1;
  }

  if (entriesSelect) {
    entriesSelect.addEventListener("change", function () {
      entriesPerPage =
        entriesSelect.value === "all"
          ? Infinity
          : parseInt(entriesSelect.value);
      currentPage = 1;
      updateTable();
    });
  }

  if (firstPageButton) {
    firstPageButton.addEventListener("click", function () {
      if (currentPage !== 1) {
        currentPage = 1;
        updateTable();
      }
    });
  }

  if (prevPageButton) {
    prevPageButton.addEventListener("click", function () {
      if (currentPage > 1) {
        currentPage--;
        updateTable();
      }
    });
  }

  if (nextPageButton) {
    nextPageButton.addEventListener("click", function () {
      tableBodies.forEach((tableBody) => {
        const rows = Array.from(tableBody.getElementsByTagName("tr"));
        if (currentPage * entriesPerPage < rows.length) {
          currentPage++;
          updateTable();
        }
      });
    });
  }

  if (lastPageButton) {
    lastPageButton.addEventListener("click", function () {
      tableBodies.forEach((tableBody) => {
        const rows = Array.from(tableBody.getElementsByTagName("tr"));
        const totalPages = Math.ceil(rows.length / entriesPerPage);
        if (currentPage !== totalPages) {
          currentPage = totalPages;
          updateTable();
        }
      });
    });
  }

  updateTable();
});

//FAQ FOR MANAGER AND USER
function toggleAnswer(answerId) {
  var answer = document.getElementById(answerId);
  if (answer.style.display === "none" || answer.style.display === "") {
    answer.style.display = "block";
  } else {
    answer.style.display = "none";
  }
}

const searchInput = document.getElementById("searchInput");
if (searchInput) {
  searchInput.addEventListener("input", function () {
    var input = this.value.toLowerCase();
    var faqItems = document.querySelectorAll(".faq-item");

    faqItems.forEach(function (item) {
      var questionText = item
        .querySelector(".question")
        .textContent.toLowerCase();
      var answer = item.querySelector(".answer");
      if (questionText.includes(input)) {
        item.style.display = "block";
      } else {
        item.style.display = "none";
      }
    });
  });
}
