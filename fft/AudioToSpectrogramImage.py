import numpy as np
import librosa
import matplotlib.pyplot as plt
import librosa.display

# MP3ファイルから音声データを読み込み


def load_audio(file_path):
    audio, sr = librosa.load(file_path, sr=None)  # サンプリングレートを自動で取得
    return audio, sr

# 周波数帯域を指定してスペクトログラムを生成


def generate_spectrogram_custom_bands(audio, sr, bands):
    # STFT（短時間フーリエ変換）
    stft = np.abs(librosa.stft(audio, n_fft=2048, hop_length=512))
    # パワースペクトログラムに変換
    spectrogram = librosa.amplitude_to_db(stft, ref=np.max)

    # 指定した周波数帯域にリサンプリング
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=2048)
    spectrogram_resampled = np.zeros((len(bands) - 1, spectrogram.shape[1]))

    for i in range(len(bands) - 1):
        # 各帯域の範囲を見つける
        freq_min = np.argmin(np.abs(frequencies - bands[i]))
        freq_max = np.argmin(np.abs(frequencies - bands[i + 1]))
        # 各帯域の平均を取る
        spectrogram_resampled[i, :] = np.mean(
            spectrogram[freq_min:freq_max, :], axis=0)

    return spectrogram_resampled

# スペクトログラムを画像として保存（ラベルあり）


def save_spectrogram_with_labels(spectrogram, sr, file_path, bands):
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(
        spectrogram, sr=sr, hop_length=512, x_axis='time', cmap='gray', y_axis=None)

    # カスタムの周波数軸を設定
    plt.yticks(np.arange(len(bands) - 1), bands[:-1])
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram with Custom Frequency Bands (Labels)')
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

# スペクトログラムを画像として保存（ラベルなし）


def save_spectrogram_no_labels(spectrogram, sr, file_path):
    plt.figure(figsize=(10, 4))
    plt.axis('off')
    librosa.display.specshow(
        spectrogram, sr=sr, hop_length=512, x_axis=None, y_axis=None, cmap='gray')
    plt.savefig(file_path, bbox_inches='tight', pad_inches=0)
    plt.close()

# メイン関数


def main(mp3_file, output_image_with_labels, output_image_no_labels):
    # 音声データを読み込み
    audio, sr = load_audio(mp3_file)

    # 指定された周波数帯域
    bands = [62, 125, 250, 500, 1000, 2000, 4000,
             8000, 16000, sr // 2]  # 最後はNyquist周波数

    # スペクトログラム生成（指定された周波数帯域）
    spectrogram = generate_spectrogram_custom_bands(audio, sr, bands)

    # スペクトログラムをラベル付きで画像として保存
    save_spectrogram_with_labels(
        spectrogram, sr, output_image_with_labels, bands)

    # スペクトログラムをラベルなしで画像として保存
    save_spectrogram_no_labels(spectrogram, sr, output_image_no_labels)


# 実行
mp3_file = 'your_audio_file.mp3'  # MP3ファイルのパス
output_image_with_labels = 'spectrogram_image_with_custom_bands_labels.png'  # ラベル付き画像のファイル名
output_image_no_labels = 'spectrogram_image_with_custom_bands_no_labels.png'  # ラベルなし画像のファイル名
main(mp3_file, output_image_with_labels, output_image_no_labels)
