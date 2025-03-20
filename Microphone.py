class AudioSource(object):
    def __init__(self):
        raise NotImplementedError("this is an abstract class")

    def __enter__(self):
        raise NotImplementedError("this is an abstract class")

    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError("this is an abstract class")


class Microphone(AudioSource):
    """
    创建一个新的“Microphone”实例，代表计算机上的物理麦克风。是“AudioSource”的子类。
    如果您没有安装PyAudio0.2.11或更高版本，将会引发“AttributeError”。
    如果未指定“device_index”或为“None”，则默认麦克风将用作音频源。否则，“device_index”应该是要用于音频输入的设备索引。
    设备索引是一个介于0和“pyaudio.get_device_count() - 1”（假设我们之前已经使用了“import pyaudio”）之间的整数。它代表音频设备，如麦克风或扬声器。有关更多详细信息，请参阅
        `PyAudio文档 < http: // people.csail.mit.edu / hubert / pyaudio / docs / > `__。
    麦克风音频以“chunk_size”个样本一组录制，在每秒“sample_rate”个样本（赫兹）的速度下。如果未指定，“sample_rate”的值将根据系统的麦克风设置自动确定。
    更高的“sample_rate”值会带来更好的音频质量，但也会消耗更多带宽（因此，识别速度较慢）。此外，一些CPU（例如旧版Raspberry Pi模型中的CPU）在此值过高时无法跟上。
    较大的“chunk_size”值有助于避免对快速变化的环境噪音产生触发，但也会使检测变得不够敏感。一般情况下，此值应该保留为默认值。
    """

    def __init__(self, device_index=None, sample_rate=None, chunk_size=1024, speaker=False, channels = 1):
        assert device_index is None or isinstance(device_index, int), "Device index must be None or an integer"
        assert sample_rate is None or (isinstance(sample_rate, int) and sample_rate > 0), "Sample rate must be None or a positive integer"
        assert isinstance(chunk_size, int) and chunk_size > 0, "Chunk size must be a positive integer"

        # set up PyAudio
        self.speaker=speaker
        self.pyaudio_module = self.get_pyaudio()
        audio = self.pyaudio_module.PyAudio()
        try:
            count = audio.get_device_count()  # obtain device count
            if device_index is not None:  # ensure device index is in range
                assert 0 <= device_index < count, "Device index out of range ({} devices available; device index should be between 0 and {} inclusive)".format(count, count - 1)
            if sample_rate is None:  # automatically set the sample rate to the hardware's default sample rate if not specified
                device_info = audio.get_device_info_by_index(device_index) if device_index is not None else audio.get_default_input_device_info()
                assert isinstance(device_info.get("defaultSampleRate"), (float, int)) and device_info["defaultSampleRate"] > 0, "Invalid device info returned from PyAudio: {}".format(device_info)
                sample_rate = int(device_info["defaultSampleRate"])
        finally:
            audio.terminate()

        self.device_index = device_index
        self.format = self.pyaudio_module.paInt16  # 16-bit int sampling
        self.SAMPLE_WIDTH = self.pyaudio_module.get_sample_size(self.format)  # size of each sample
        self.SAMPLE_RATE = sample_rate  # sampling rate in Hertz
        self.CHUNK = chunk_size  # number of frames stored in each buffer
        self.channels = channels

        self.audio = None
        self.stream = None

    @staticmethod
    def get_pyaudio():
        """
        导入 pyaudio 模块并检查其版本。如果找不到 pyaudio 或安装了错误的版本，则引发异常
        """
        try:
            import pyaudiowpatch as pyaudio
        except ImportError:
            raise AttributeError("Could not find PyAudio; check installation")
        return pyaudio

    def __enter__(self):
        assert self.stream is None, "他的音频源已经在 Context Manager 中"
        self.audio = self.pyaudio_module.PyAudio()

        try:
            if self.speaker:
                p = self.audio
                self.stream = Microphone.MicrophoneStream(
                    p.open(
                        input_device_index=self.device_index,
                        channels=self.channels,
                        format=self.format,
                        rate=self.SAMPLE_RATE,
                        frames_per_buffer=self.CHUNK,
                        input=True
                    )
                )
            else:
                self.stream = Microphone.MicrophoneStream(
                    self.audio.open(
                        input_device_index=self.device_index, channels=1, format=self.format,
                        rate=self.SAMPLE_RATE, frames_per_buffer=self.CHUNK, input=True,
                    )
                )
        except Exception:
            self.audio.terminate()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.stream.close()
        finally:
            self.stream = None
            self.audio.terminate()

    class MicrophoneStream(object):
        def __init__(self, pyaudio_stream):
            self.pyaudio_stream = pyaudio_stream

        def read(self, size):
            return self.pyaudio_stream.read(size, exception_on_overflow=False)

        def close(self):
            try:
                # 有时，如果流未停止，则关闭流会引发异常
                if not self.pyaudio_stream.is_stopped():
                    self.pyaudio_stream.stop_stream()
            finally:
                self.pyaudio_stream.close()

