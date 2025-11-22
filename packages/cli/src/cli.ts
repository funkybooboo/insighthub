#!/usr/bin/env node

import { runCommand } from './commands';

console.log('Welcome to InsightHub CLI!');

const args = process.argv.slice(2);
runCommand(args);
