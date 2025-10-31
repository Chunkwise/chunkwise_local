import app from "./app";
import config from "./config/config";

const PORT = config.port;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT} in ${config.nodeEnv} mode.`);
});
