from datadog_checks.base import AgentCheck
import os, time

__version__ = "1.0.0"

class DEMOCM(AgentCheck):
    def check(self, instance):
        count=0
        dir_path = "C:\ProgramData\Datadog\test"
        for path in os.listdir(dir_path):
            if (int(time.time()) - int(os.path.getctime(os.path.join(dir_path, path))) < 60):
                count+=1
        print(count)
        self.count(
            "file.modified.count",
            count,
            tags=["env:local","app:modified_file_count"],
        )
        
        self.count(
            "file.modified.count",
            count,
            tags=["key1:valu11"],
        )