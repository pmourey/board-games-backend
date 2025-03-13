For macOS **10.15 Catalina**, the correct SDK version is **MacOSX10.15.sdk**.  

You can download it from:  
🔗 [MacOSX10.15.sdk on GitHub](https://github.com/phracker/MacOSX-SDKs/releases/tag/10.15)  

### Steps to Install:
1. **Download the SDK** (`MacOSX10.15.sdk.tar.xz`) from the link above.
2. **Extract it**:
   ```sh
   tar -xJf MacOSX10.15.sdk.tar.xz
   ```
3. **Move it to the correct location**:
   ```sh
   sudo mv MacOSX10.15.sdk /Library/Developer/CommandLineTools/SDKs/
   ```
4. **Set the SDK path before compiling Stockfish**:
   ```sh
   export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX10.15.sdk
   ```

Now, try compiling Stockfish again. Let me know if you need further help! 🚀