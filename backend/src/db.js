const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, '../containerguard.db');

let db = null;

function initDB() {
  return new Promise((resolve, reject) => {
    db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('Database connection error:', err);
        reject(err);
      } else {
        console.log('✅ SQLite database connected');
        
        // Create users table
        db.run(`
          CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `, (err) => {
          if (err) {
            console.error('Table creation error:', err);
            reject(err);
          } else {
            console.log('✅ Users table ready');
            resolve(db);
          }
        });
      }
    });
  });
}

function getDB() {
  if (!db) throw new Error('Database not initialized');
  return db;
}

function closeDB() {
  if (db) db.close();
}

module.exports = { initDB, getDB, closeDB };
