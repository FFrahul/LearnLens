"""Small, opt-in local LSTM experiment over learner quiz history."""


def run_keras_dnn_experiment(history, minimum_samples=20, epochs=5):
    """Lazy wrapper for the optional TensorFlow/Keras DNN implementation."""
    from tensorflow_experiment import run_keras_dnn_experiment as run
    return run(history, minimum_samples=minimum_samples, epochs=epochs)


def run_keras_lstm_experiment(history, minimum_samples=20, epochs=5):
    """Lazy wrapper for the optional TensorFlow/Keras LSTM implementation."""
    from tensorflow_experiment import run_keras_lstm_experiment as run
    return run(history, minimum_samples=minimum_samples, epochs=epochs)


run_tensorflow_dnn_experiment = run_keras_dnn_experiment
run_tensorflow_lstm_experiment = run_keras_lstm_experiment
run_dnn_experiment_tensorflow = run_keras_dnn_experiment
run_lstm_experiment_tensorflow = run_keras_lstm_experiment


def run_lstm_experiment(history, minimum_samples=20, epochs=5):
    from experiment_readiness import assess_sequence_readiness

    readiness = assess_sequence_readiness(
        history,
        minimum_samples=minimum_samples
    )
    if not readiness["ready"]:
        return {
            "ready": False,
            "readiness": readiness,
            "message": "More labeled learner history is required.",
        }

    try:
        import torch
        from torch import nn
    except ImportError:
        return {
            "ready": False,
            "readiness": readiness,
            "message": "PyTorch is not installed.",
        }

    torch.manual_seed(7)
    values = torch.tensor(
        [
            [
                1.0 if item.get("is_correct") else 0.0,
                float({"Easy": 0.0, "Medium": 0.5, "Hard": 1.0}.get(
                    item.get("difficulty"),
                    0.5
                )),
            ]
            for item in history
            if isinstance(item, dict)
        ],
        dtype=torch.float32
    )
    inputs = values[:-1].unsqueeze(0)
    targets = values[1:, 0].unsqueeze(0).unsqueeze(-1)

    class MasteryLSTM(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(2, 8, batch_first=True)
            self.output = nn.Linear(8, 1)

        def forward(self, sequence):
            hidden, _ = self.lstm(sequence)
            return self.output(hidden)

    model = MasteryLSTM()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_function = nn.BCEWithLogitsLoss()
    final_loss = 0.0
    for _ in range(max(1, epochs)):
        optimizer.zero_grad()
        loss = loss_function(model(inputs), targets)
        loss.backward()
        optimizer.step()
        final_loss = float(loss.detach().item())

    with torch.no_grad():
        prediction = float(torch.sigmoid(model(inputs[:, -1:])).item())
    return {
        "ready": True,
        "readiness": readiness,
        "final_loss": round(final_loss, 4),
        "next_correct_probability": round(prediction, 4),
        "epochs": max(1, epochs),
        "device": "cpu",
    }


def run_dnn_experiment(history, minimum_samples=20, epochs=5):
    """Train a small feed-forward baseline on learner history."""
    from experiment_readiness import assess_sequence_readiness

    readiness = assess_sequence_readiness(
        history,
        minimum_samples=minimum_samples
    )
    if not readiness["ready"]:
        return {
            "ready": False,
            "readiness": readiness,
            "message": "More labeled learner history is required.",
        }

    try:
        import torch
        from torch import nn
    except ImportError:
        return {
            "ready": False,
            "readiness": readiness,
            "message": "PyTorch is not installed.",
        }

    torch.manual_seed(7)
    rows = [
        [
            1.0 if item.get("is_correct") else 0.0,
            float({"Easy": 0.0, "Medium": 0.5, "Hard": 1.0}.get(
                item.get("difficulty"),
                0.5
            )),
        ]
        for item in history
        if isinstance(item, dict)
    ]
    inputs = torch.tensor(rows[:-1], dtype=torch.float32)
    targets = torch.tensor(
        [[1.0 if item.get("is_correct") else 0.0] for item in history[1:]],
        dtype=torch.float32
    )
    model = nn.Sequential(
        nn.Linear(2, 8),
        nn.ReLU(),
        nn.Linear(8, 1)
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_function = nn.BCEWithLogitsLoss()
    final_loss = 0.0
    for _ in range(max(1, epochs)):
        optimizer.zero_grad()
        loss = loss_function(model(inputs), targets)
        loss.backward()
        optimizer.step()
        final_loss = float(loss.detach().item())

    with torch.no_grad():
        prediction = float(torch.sigmoid(model(inputs[-1:])).item())
    return {
        "ready": True,
        "readiness": readiness,
        "final_loss": round(final_loss, 4),
        "next_correct_probability": round(prediction, 4),
        "epochs": max(1, epochs),
        "device": "cpu",
    }
