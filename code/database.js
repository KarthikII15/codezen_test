/**
 * @file Manages the connection to the MongoDB database using Mongoose.
 * This module handles initial connection establishment, listens for connection events,
 * and ensures graceful termination upon application shutdown signals.
 */
const mongoose = require('mongoose');
const dotenv = require('dotenv');

dotenv.config();

/**
 * Establishes a connection to MongoDB using Mongoose.
 * This function relies on the MONGODB_URI environment variable for the connection string.
 * If the connection fails, it logs an error and terminates the application process with exit code 1.
 * @returns {Promise<void>} A Promise that resolves when the connection is successfully established.
 */
const connectDB = async () => {
  try {
    const mongoURI = process.env.MONGODB_URI;
    const conn = await mongoose.connect(mongoURI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`Error connecting to MongoDB:`, error);
    process.exit(1);
  }
};

// Listen for MongoDB connection events
mongoose.connection.on('error', (err) => {
  console.error(`MongoDB connection error: ${err}`);
});

mongoose.connection.on('disconnected', () => {
  console.log(`MongoDB disconnected`);
});

// Handle app termination gracefully
process.on('SIGINT', async () => {
  try {
    await mongoose.connection.close();
    console.log(`MongoDB connection closed through app termination`);
    process.exit(0);
  } catch (error) {
    console.error(`Error during MongoDB connection closure:`, error);
    process.exit(1);
  }
});

module.exports = connectDB; 
