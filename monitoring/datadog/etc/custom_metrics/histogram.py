from datadog_checks.base import AgentCheck
import os, time

__version__ = "1.0.0"

class DEMOCM(AgentCheck):
    def check(self, instance):
        count=0
        dir_path = "C:\\ProgramData\\Datadog\\test"
        for path in os.listdir(dir_path):
            if (int(time.time()) - int(os.path.getctime(os.path.join(dir_path, path))) < 60):
                count+=1
        print(count)
        
        for i in range(6):
            self.histogram(
                "file.modified.histogram",
                count,
                tags=["env:local","app:file_count_hist"],
            )
        time.sleep(10)
