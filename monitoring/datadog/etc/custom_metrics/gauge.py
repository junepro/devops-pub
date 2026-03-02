from datadog_checks.base import AgentCheck
import os, time

__version__ = "1.0.0"

class DEMOCM(AgentCheck):
    def check(self, instance):
        count=0
        dir_path = "C:\\ProgramData\\Datadog\\test"      
        
        for i in range(6):
     
            # Iterate directory
            for path in os.listdir(dir_path):
                # check if current path is a file
                if os.path.isfile(os.path.join(dir_path, path)):
                    count += 1
               
            self.gauge("directory.file.count", count,tags=["env:local","app:final_file_count"],)    
            sleep(10)