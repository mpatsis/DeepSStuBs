const fs = require("fs");
const util = require("./jsExtractionUtil");


const code = fs.readFileSync(path);
const tokens = util.getTokens(code);
if (tokens) {
    console.log(util.tokensToStrings(tokens));
} else {
    console.log("Ignoring file with parse errors: " + path);
}

