from multiprocessing import shared_memory as shm
for i in range(30):
    try:
        m = shm.SharedMemory(name=f"pacemaker_{i}_")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"pacemaker_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"ReadOpenEphys_{i}_")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"ReadOpenEphys_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"FFT_BandPowerPlot_{i}_")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"FFT_BandPowerPlot_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"simpleThreshold_{i}_")
        m.close()
        m.unlink()
    except: 
        pass
    try:
        m = shm.SharedMemory(name=f"simpleThreshold_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"SignalDisp_{i}_")
        m.close()
        m.unlink()
    except:
        pass
    try:    
        m = shm.SharedMemory(name=f"SignalDisp_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"bandpower_logger_{i}_")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"bandpower_logger_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"stim_logger_{i}_")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"stim_logger_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"curve_plotter_{i}_")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"curve_plotter_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"rec_timestamp_logger_{i}_")
        m.close()
        m.unlink()
    except:
        pass
    try:
        m = shm.SharedMemory(name=f"rec_timestamp_logger_{i}__")
        m.close()
        m.unlink()
    except:
        pass
    