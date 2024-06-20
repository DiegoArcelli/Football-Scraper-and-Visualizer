const express = require('express')
const path = require('path');
const app = express()
const port = 3000

app.get('/', function(req, res) {
    res.sendFile(path.join(__dirname, '/html/team_page.html'));
});

app.post('/query', function(req, res) {
    console.log(req)
    //const sqlite3 = require('sqlite3').verbose();
    //const db = new sqlite3.Database(':memory:');
});

app.listen(port, () => {
    console.log(`App listening on port ${port}`);
});