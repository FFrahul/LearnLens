"""Optional TensorFlow/Keras sequence experiments.

TensorFlow is imported only when one of these functions is called.  The module
itself, and the rest of the application, remain usable without TensorFlow.
"""


def _build_rows(history):
    rows = []
    difficulty = {"Easy": 0.0, "Medium": 0.5, "Hard": 1.0}
    for item in history:
        if not isinstance(item, dict):
            continue
        rows.append([
            1.0 if item.get("is_correct") else 0.0,
            float(difficulty.get(item.get("difficulty"), 0.5)),
        ])
    return rows


def _prepare(history, minimum_samples):
    from experiment_readiness import assess_sequence_readiness

    readiness = assess_sequence_readiness(
        history,
        minimum_samples=minimum_samples,
    )
    if not readiness["ready"]:
        return readiness, None, None

    rows = _build_rows(history)
    if len(rows) < 2:
        return {
            "ready": False,
            "samples": len(rows),
            "topics": readiness["topics"],
            "reasons": ["Need at least 2 labeled observations."],
        }, None, None

    try:
        import numpy as np
    except ImportError:
        return readiness, None, "NumPy is not installed."

    inputs = np.asarray(rows[:-1], dtype="float32")
    targets = np.asarray(
        [[rows[index][0]] for index in range(1, len(rows))],
        dtype="float32",
    )
    return readiness, (inputs, targets), None


def _load_tensorflow():
    try:
        import tensorflow as tf
        from tensorflow import keras
    except (ImportError, ModuleNotFoundError):
        return None, "TensorFlow/Keras is not installed."
    except Exception as exc:
        return None, "TensorFlow/Keras could not be loaded: {}.".format(exc)
    return (tf, keras), None


def run_keras_dnn_experiment(history, minimum_samples=20, epochs=5):
    """Train a small isolated TensorFlow/Keras feed-forward baseline."""
    from experiment_readiness import assess_sequence_readiness

    readiness = assess_sequence_readiness(history, minimum_samples)
    if not readiness["ready"]:
        return {
            "ready": False,
            "readiness": readiness,
            "message": "More labeled learner history is required.",
        }

    tensorflow, load_error = _load_tensorflow()
    if load_error:
        return {
            "ready": False,
            "readiness": readiness,
            "message": load_error,
        }

    readiness, prepared, prep_error = _prepare(history, minimum_samples)
    if prep_error:
        return {"ready": False, "readiness": readiness, "message": prep_error}
    if not prepared:
        return {
            "ready": False,
            "readiness": readiness,
            "message": "More labeled learner history is required.",
        }

    tf, keras = tensorflow
    tf.keras.utils.set_random_seed(7)
    inputs, targets = prepared
    model = keras.Sequential([
        keras.layers.Input(shape=(2,), name="learner_features"),
        keras.layers.Dense(8, activation="relu"),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.01),
        loss="binary_crossentropy",
    )
    result = model.fit(
        inputs,
        targets,
        epochs=max(1, epochs),
        verbose=0,
    )
    final_loss = float(result.history["loss"][-1])
    prediction = float(model.predict(inputs[-1:], verbose=0)[0, 0])
    return {
        "ready": True,
        "readiness": readiness,
        "final_loss": round(final_loss, 4),
        "next_correct_probability": round(prediction, 4),
        "epochs": max(1, epochs),
        "device": "cpu",
        "framework": "tensorflow",
    }


def run_keras_lstm_experiment(history, minimum_samples=20, epochs=5):
    """Train a small isolated TensorFlow/Keras LSTM experiment."""
    from experiment_readiness import assess_sequence_readiness

    readiness = assess_sequence_readiness(history, minimum_samples)
    if not readiness["ready"]:
        return {
            "ready": False,
            "readiness": readiness,
            "message": "More labeled learner history is required.",
        }

    tensorflow, load_error = _load_tensorflow()
    if load_error:
        return {
            "ready": False,
            "readiness": readiness,
            "message": load_error,
        }

    readiness, prepared, prep_error = _prepare(history, minimum_samples)
    if prep_error:
        return {"ready": False, "readiness": readiness, "message": prep_error}
    if not prepared:
        return {
            "ready": False,
            "readiness": readiness,
            "message": "More labeled learner history is required.",
        }

    tf, keras = tensorflow
    tf.keras.utils.set_random_seed(7)
    inputs, targets = prepared
    sequence_inputs = inputs.reshape((1, inputs.shape[0], 2))
    sequence_targets = targets.reshape((1, targets.shape[0], 1))
    model = keras.Sequential([
        keras.layers.Input(shape=(None, 2), name="learner_sequence"),
        keras.layers.LSTM(8),
        keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.01),
        loss="binary_crossentropy",
    )
    result = model.fit(
        sequence_inputs,
        sequence_targets[:, -1:, :],
        epochs=max(1, epochs),
        verbose=0,
    )
    final_loss = float(result.history["loss"][-1])
    prediction = float(model.predict(sequence_inputs[:, -1:, :], verbose=0)[0, 0])
    return {
        "ready": True,
        "readiness": readiness,
        "final_loss": round(final_loss, 4),
        "next_correct_probability": round(prediction, 4),
        "epochs": max(1, epochs),
        "device": "cpu",
        "framework": "tensorflow",
    }


# Descriptive aliases for callers that identify the framework explicitly.
run_tensorflow_dnn_experiment = run_keras_dnn_experiment
run_tensorflow_lstm_experiment = run_keras_lstm_experiment
run_dnn_experiment = run_keras_dnn_experiment
run_lstm_experiment = run_keras_lstm_experiment
