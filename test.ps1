1..30 | ForEach-Object {
  Invoke-WebRequest http://localhost:8000/ -UseBasicParsing | Out-Null
  Invoke-WebRequest "http://localhost:8000/work?seconds=0.5" -UseBasicParsing | Out-Null
}

1..5 | ForEach-Object {
  try {
    Invoke-WebRequest http://localhost:8000/fail -UseBasicParsing | Out-Null
  } catch {
    # Expected: this endpoint returns HTTP 500.
  }
}