#!/usr/bin/env node

console.log("Welcome to InsightHub CLI!");

const args = process.argv.slice(2);

if (args.length > 0) {
  console.log("Arguments:", args.join(", "));
} else {
  console.log("No arguments provided.");
}
