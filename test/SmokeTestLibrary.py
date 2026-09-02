import subprocess


class SmokeTestLibrary:
    """Keywords used by the cross-machine Robot Framework smoke test."""

    def framework_is_available(self):
        return True

    def pcberry_is_available(self):
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "pcberry.local"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
                check=False,
            )
            print(f"Ping result: {result.returncode}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

        return True if result.returncode == 0 else False