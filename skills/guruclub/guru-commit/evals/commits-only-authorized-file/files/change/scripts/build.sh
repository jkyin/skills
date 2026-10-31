#!/usr/bin/env bash
set -eu
xcodebuild -workspace GuruClub.xcworkspace -scheme GuruClub -configuration Debug build
