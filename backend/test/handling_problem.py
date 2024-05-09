class T:
    def __init__(self) -> None:
        pass
    
    def test(self, raw):
        print(raw)
        
Test = T
sd = Test()

func = getattr(sd, "test")
func(raw = "afe")