<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SignalCheck</title>
  <style>
    body {
      width: 320px;
      padding: 15px;
      font-family: Arial, sans-serif;
      background: #f4f6f9;
    }

    h2 {
      margin: 0 0 5px 0;
    }

    p {
      font-size: 13px;
      margin: 0 0 10px 0;
      color: #555;
    }

    .error {
      color: #d32f2f;
      margin: 10px 0;
      font-size: 13px;
    }

    .result {
      margin-top: 15px;
      font-size: 13px;
    }

    .status {
      padding: 8px;
      border-radius: 6px;
      text-align: center;
      font-weight: bold;
      margin-bottom: 8px;
    }

    .green {
      background-color: #e8f5e9;
      color: #2e7d32;
    }

    .yellow {
      background-color: #fff8e1;
      color: #ef6c00;
    }

    .red {
      background-color: #ffebee;
      color: #c62828;
    }

    button {
      width: 100%;
      padding: 10px;
      border: none;
      border-radius: 8px;
      background: #1e88e5;
      color: white;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.2s ease;
      margin-top: 10px;
    }

    button:hover {
      background: #1565c0;
    }

    button:active {
      transform: scale(0.98);
    }

    ul {
      padding-left: 18px;
      margin: 5px 0 0 0;
    }
  </style>
</head>
<body>

  <h2>SignalCheck</h2>
  <p>Análisis contextual de la información</p>

  <div id="error" class="error" style="display: none;"></div>

  <div id="result" class="result" style="display: none;">
    <div class="status" id="status"></div>
    <p><strong>Puntaje:</strong> <span id="score"></span></p>
    <p><strong>Señales detectadas:</strong></p>
    <ul id="signals"></ul>
  </div>

  <button id="analyzeBtn">Analizar página</button>

  <script src="popup.js"></script>

</body>
</html>
